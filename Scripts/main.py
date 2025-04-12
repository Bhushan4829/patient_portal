from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from views import router as views_router
from appointment import router as appointment_router
from chat import router as chat_router

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(views_router)
app.include_router(appointment_router, prefix="/appointment")
app.include_router(chat_router, prefix="/chat")
