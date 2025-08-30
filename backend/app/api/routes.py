# app/api/routes.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from datetime import datetime
from typing import Dict, Any
from app.schemas import QueryRequest, QueryResponse
from app.services.documents import summarize_document
from app.services.weather import WeatherService
from app.agents.maritime_agent import MaritimeLangChainAgent
from dotenv import load_dotenv
import os
import asyncio

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

# Initialize router and agent
router = APIRouter()
maritime_agent = MaritimeLangChainAgent(api_key=api_key)

# -------------------------
# Health Check
# -------------------------
@router.get("/ping")
async def ping():
    return {"status": "ok"}

# -------------------------
# Ask Agent
# -------------------------
@router.post("/ask", response_model=QueryResponse)
async def ask_agent(req: QueryRequest):
    try:
        # Await async process_query
        result = await maritime_agent.process_query(req.query)

        # If result is string, wrap into dict
        if isinstance(result, str):
            result = {
                "answer": result,
                "tools_used": [],
                "execution_plan": "N/A",
                "confidence": 1.0,
                "timestamp": datetime.now().isoformat()
            }

        return QueryResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

# -------------------------
# Summarize Document
# -------------------------
@router.post("/documents/summarize", response_model=QueryResponse)
async def summarize_uploaded_file(file: UploadFile = File(...)):
    try:
        summary = await summarize_document(file)
        return QueryResponse(answer=summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error summarizing document: {str(e)}")

# -------------------------
# Weather Endpoint
# -------------------------
@router.get("/weather/{lat}/{lon}")
async def get_weather(lat: float, lon: float):
    try:
        service = WeatherService()

        # Run blocking calls in a separate thread
        forecast = await asyncio.to_thread(service.get_weather_forecast, lat, lon)
        bad_periods = await asyncio.to_thread(service.get_bad_weather_periods, lat, lon)

        return {
            "forecast": forecast,
            "bad_periods": bad_periods
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching weather: {str(e)}")

# -------------------------
# Agent Status
# -------------------------
@router.get("/agent/status")
async def agent_status():
    try:
        status = await asyncio.to_thread(maritime_agent.get_agent_status)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching agent status: {str(e)}")
