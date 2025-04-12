from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from db import get_db_connection
import tempfile
import os
import shutil
import pandas as pd
import torch
from PIL import Image
from torchvision import transforms
import openai
import configparser
from torchvision.models import resnet50, ResNet50_Weights
router = APIRouter()

# Configuration
config = configparser.ConfigParser()
config.read('db_config.ini')
openai.api_key = config['openai']['api_key']

# Load Data Entry labels
data_entry = pd.read_csv("../Data_Entry_2017.csv")
all_labels = sorted(set(label for sublist in data_entry['Finding Labels'].str.split('|') for label in sublist))

# Load model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = resnet50(weights=None) 
model.fc = torch.nn.Sequential(
    torch.nn.Linear(model.fc.in_features, len(all_labels)),
    torch.nn.Sigmoid()
)
model.load_state_dict(torch.load("../best_model.pth", map_location=torch.device('cpu')))
model.to(device)
model.eval()

# Image preprocessing
tfms = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

def fetch_patient_data(patient_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    data = {}
    try:
        tables = {
            'allergies': 'SELECT START, STOP, SYSTEM, DESCRIPTION, CATEGORY, REACTION1, DESCRIPTION1, SEVERITY1, REACTION2, DESCRIPTION2, SEVERITY2 FROM allergies WHERE PATIENT = ?',
            'conditions': 'SELECT START, STOP, DESCRIPTION FROM conditions WHERE PATIENT = ?',
            'encounters': 'SELECT START, STOP, DESCRIPTION FROM encounters WHERE PATIENT = ?',
            'imaging studies': 'SELECT DATE, BODYSITE_DESCRIPTION, MODALITY_DESCRIPTION, SOP_DESCRIPTION FROM imaging_studies WHERE PATIENT = ?',
            'immunizations': 'SELECT DATE , DESCRIPTION FROM immunizations WHERE PATIENT = ?',
            'medications': 'SELECT START, STOP, DESCRIPTION, REASONDESCRIPTION FROM medications WHERE PATIENT = ?',
            'observations': 'SELECT DATE, DESCRIPTION,CATEGORY, TYPE FROM observations WHERE PATIENT = ?'
        }
        for key, q in tables.items():
            cursor.execute(q, (patient_id,))
            results = cursor.fetchall()
            data[key] = [dict(zip([col[0] for col in cursor.description], row)) for row in results]

        cursor.execute('SELECT FIRST, LAST FROM patients WHERE Id = ?', (patient_id,))
        name = cursor.fetchone()
        data['name'] = f"{name[0]} {name[1]}" if name else "Unnamed Patient"
    except Exception as e:
        print(f"Error fetching patient data: {str(e)}")
        data = {}
    finally:
        cursor.close()
        conn.close()
    return data

def create_prompt(patient_id, patient_data, xray_analysis):
    name = patient_data.pop('name', 'Unnamed Patient')
    context = [f"Patient ID {patient_id}, {name}, has the following medical record:"]
    for cat, entries in patient_data.items():
        context.append(f"{cat.upper()}:")
        for e in entries:
            desc = ', '.join(f"{k}={v}" for k, v in e.items() if v)
            context.append(desc)
    context.append(f"X-RAY ANALYSIS: {xray_analysis}")
    prompt = f"As a medical assistant, you need to consider the following data to provide the best advice: {' '.join(context)}"
    return prompt

def analyze_xray(img_path):
    img = Image.open(img_path).convert('RGB')
    img = tfms(img).unsqueeze(0).to(device)
    with torch.no_grad():
        output = model(img)
        probs, idx = torch.max(output, 1)
        predicted_class = all_labels[idx.item()]
        predicted_prob = torch.sigmoid(probs).item()
    return f"Predicted Condition: {predicted_class} with probability {predicted_prob:.2%}"

@router.post("/{patient_id}")
async def chat(patient_id: str, message: str = Form(...), file: UploadFile = File(None)):
    image_path = None
    temp_dir = tempfile.mkdtemp()
    try:
        xray_result = "No X-ray image provided."
        if file:
            image_path = os.path.join(temp_dir, file.filename)
            with open(image_path, "wb") as f:
                f.write(await file.read())
            xray_result = analyze_xray(image_path)

        patient_data = fetch_patient_data(patient_id)
        if not patient_data:
            raise HTTPException(status_code=500, detail="Failed to fetch patient data")

        prompt = create_prompt(patient_id, patient_data, xray_result)
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": message},
        ]

        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=150
        )
        assistant_msg = response.choices[0].message.content.strip() if response.choices else "No response from model."
        return JSONResponse(content={"response": assistant_msg})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Chatbot failed: {str(e)}"})
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
