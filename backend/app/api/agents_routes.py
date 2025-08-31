# app/api/agent_router.py
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
import json
from app.agents.maritime_agent import MaritimeLangChainAgent
from app.services.documents import summarize_document
from dotenv import load_dotenv
import os
import asyncio

# Load environment
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

# Initialize router and agent
agent_router = APIRouter()
maritime_agent = MaritimeLangChainAgent(api_key=api_key)

# -------------------------
# Response model
# -------------------------
class AgentQueryResponse(BaseModel):
    answer: Optional[str] = None
    tools_used: Optional[List[str]] = None
    execution_plan: Optional[str] = None
    confidence: Optional[float] = None
    timestamp: Optional[str] = None
    error: Optional[str] = None   # ✅ Added error field

# -------------------------
# Agent Query Route
# -------------------------
@agent_router.post("/agent/query", response_model=AgentQueryResponse)
async def agentic_query(
    query: str = Form(...),
    file: Optional[UploadFile] = File(None),
    context: Optional[str] = Form(None)
):
    try:
        # Parse context
        context_dict = {}
        if context:
            try:
                context_dict = json.loads(context)
            except:
                context_dict = {"note": context}

        # Summarize uploaded document if present
        if file:
            summary = await summarize_document(file)
            query = f"{query}\n\nDocument summary: {summary}"

        # Await the async process_query coroutine
        result = await maritime_agent.process_query(query)

        # Normalize result to match schema
        if isinstance(result, str):
            result = {
                "answer": result,
                "tools_used": [],
                "execution_plan": "N/A",
                "confidence": 1.0,
                "timestamp": datetime.now().isoformat()
            }
        elif isinstance(result, dict) and "error" in result:
            # ✅ If agent returned an error dict
            result = {
                "error": result.get("error"),
                "timestamp": datetime.now().isoformat()
            }

        return AgentQueryResponse(**result)

    except Exception as e:
        # ✅ Capture unexpected errors in schema too
        return AgentQueryResponse(
            error=f"Agent processing error: {str(e)}",
            timestamp=datetime.now().isoformat()
        )

# -------------------------
# Agent Status Route
# -------------------------
@agent_router.get("/agent/status")
async def get_agent_status():
    try:
        status = await asyncio.to_thread(maritime_agent.get_agent_status)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching agent status: {str(e)}")

# -------------------------
# Clear Memory Route
# -------------------------
@agent_router.post("/agent/memory/clear")
async def clear_agent_memory():
    try:
        result = await asyncio.to_thread(maritime_agent.clear_memory)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing memory: {str(e)}")
