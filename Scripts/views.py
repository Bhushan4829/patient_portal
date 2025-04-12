from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from db import get_mimiciv_db_connection
from summary import generate_patient_summary
import hashlib

router = APIRouter()

class AuthRequest(BaseModel):
    family_name: str
    birth_date: str
    identifier_value: str

@router.post("/login")
async def login(auth: AuthRequest):
    raw_password = f"{auth.birth_date}{auth.family_name}"
    salted_input = f"{auth.identifier_value}:{raw_password}"
    expected_hash = hashlib.sha256(salted_input.encode('utf-8')).hexdigest()

    print("Expected Hash:", expected_hash)

    cnxn = get_mimiciv_db_connection()
    cursor = cnxn.cursor()
    cursor.execute("""
        SELECT user_id, patient_id, hashed_password 
        FROM auth_user 
        WHERE name = ? AND user_id = ?
    """, (auth.family_name, auth.identifier_value))
    user = cursor.fetchone()
    cursor.close()
    cnxn.close()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db_hash = user.hashed_password
    print("DB hash:", db_hash)

    if db_hash == expected_hash:
        return {"message": "Login successful", "patient_id": user.patient_id}
    
    raise HTTPException(status_code=401, detail="Invalid credentials")


@router.post("/signup")
async def signup(auth: AuthRequest):
    raw_password = f"{auth.birth_date}{auth.family_name}"
    print(f"Raw password: {raw_password}")
    salted_input = f"{auth.identifier_value}:{raw_password}"
    print(f"Salted input: {salted_input}")
    hashed_password = hashlib.sha256(salted_input.encode('utf-8')).hexdigest()

    cnxn = get_mimiciv_db_connection()
    cursor = cnxn.cursor()

    try:
        cursor.execute("SELECT id FROM auth_user WHERE identifier_value = ?", (auth.identifier_value,))
        if cursor.fetchone():
            raise HTTPException(status_code=409, detail="User already exists")

        cursor.execute("""
            INSERT INTO auth_user (name, identifier_value, birthDate, raw_password, hashed_password, role, created_at)
            VALUES (?, ?, ?, ?, ?, 'patient', CURRENT_TIMESTAMP)
        """, (auth.family_name, auth.identifier_value, auth.birth_date, raw_password, hashed_password))
        cnxn.commit()
        return {"message": "Signup successful", "patient_id": cursor.lastrowid}
    finally:
        cursor.close()
        cnxn.close()

@router.get("/logout")
async def logout():
    return {"message": "Logged out successfully"}

@router.get("/patient_data/{patient_id}")
async def get_patient_data(patient_id: str):
    cnxn = get_mimiciv_db_connection()
    cursor = cnxn.cursor()
    cursor.execute("""
        SELECT id AS patient_id, name_family, gender, birthDate, identifier_value,
               communication_language_coding_code, maritalStatus_coding_code, deceasedDateTime
        FROM mimicpatient_demographics
        WHERE id = ?
    """, (patient_id,))
    row = cursor.fetchone()
    cursor.close()
    cnxn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Patient not found")
    col_names = [desc[0] for desc in cursor.description]
    patient_data = dict(zip(col_names, row))
    return {"summary": generate_patient_summary(patient_data), "Details": patient_data}
