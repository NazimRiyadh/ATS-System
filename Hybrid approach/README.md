# ATS Hybrid Pipeline - Full Stack Application

## Overview
This is a production-ready Applicant Tracking System (ATS) that combines **Vector Search** and **Graph Database** technologies. It features a modern Next.js frontend and a FastAPI backend.

## Features
- **Hybrid Search**: Semantic search + Hard filters (Skills, Experience, Location).
- **RAG Chatbot**: Chat with candidate profiles to ask specific questions.
- **Feedback Loop**: System learns from user interactions (clicks/likes) to improve ranking.
- **Modern UI**: Responsive dashboard built with Next.js and Tailwind CSS.

## Prerequisites
- Python 3.8+
- Node.js 18+
- Neo4j Database (Running)
- OpenAI API Key (in `.env`)

## Quick Start

### 1. Start the Backend API
The backend handles search, ingestion, and AI logic.
```bash
# Install dependencies
pip install -r requirements.txt
pip install fastapi uvicorn pydantic

# Run the server (Port 8001)
uvicorn api.main:app --host 0.0.0.0 --port 8001 --reload
```
*API Docs available at: http://localhost:8001/docs*

### 2. Start the Frontend
The frontend provides the user interface.
```bash
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```
*Open http://localhost:3000 in your browser.*

## Usage Guide
1.  **Ingest Candidates**: Use the API `/ingest` endpoint or the CLI scripts in `examples/` to add resumes.
2.  **Search**: Go to the frontend, type a query (e.g., "Python Expert"), and apply filters.
3.  **Chat**: Click "Chat with Profile" on any candidate card to ask questions about them.
4.  **Feedback**: Click Thumbs Up/Down to help the system learn.

## Architecture
- **Backend**: FastAPI, Neo4j Driver, OpenAI Client
- **Frontend**: Next.js 14, Tailwind CSS, Lucide Icons
- **Database**: Neo4j (Graph + Vector Index)
