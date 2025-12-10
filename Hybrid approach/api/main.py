"""
FastAPI Backend for ATS Pipeline
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ATS Hybrid Pipeline API",
    description="API for Applicant Tracking System with Hybrid Search and RAG",
    version="2.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "ATS Hybrid Pipeline API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
