import asyncio
import time

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.agents.llm import call_llm
from app.database import get_db
from app.models.incident import Incident

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatMessage(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    time: str


@router.post("/{incident_id}")
async def chat_with_ai(incident_id: str, payload: ChatMessage, db: Session = Depends(get_db)):
    """Conversational interface for an incident."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    prompt = f"""
    You are IncidentOps AI, an expert SRE assistant helping an engineer investigate an incident.
    Be concise, helpful, and direct. Use the following context to answer the user's question.

    Incident Context:
    - ID: {incident.id}
    - Title: {incident.title}
    - Service: {incident.service}
    - Status: {incident.status}
    - Root Cause Analysis: {incident.resolution_summary or "Not yet completed"}

    User Question: {payload.message}
    """

    # Simulate thinking delay
    await asyncio.sleep(1.5)

    reply = await call_llm(system_prompt=prompt, user_prompt=payload.message)

    return ChatResponse(reply=reply, time=time.strftime("%H:%M:%S") if "time" in globals() else "Just now")
