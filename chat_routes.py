"""
Chat API Router (APIRouter)
----------------------------
Encapsulates RESTful endpoints for the Universal Agentic Claims Chatbot:
  - POST /api/chat/message     : Send prompt and receive LLM reply with tool execution & cited claims
  - POST /api/chat/reset       : Reset multi-turn conversation memory for a session
  - GET  /api/chat/suggestions : Quick-start prompt chips for adjusters
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, status

from chatbot_engine import process_chat_message, reset_session

chat_router = APIRouter(prefix="/api/chat", tags=["Adjuster AI Copilot Chat"])


class ChatMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Natural language question or command")
    session_id: Optional[str] = Field("default_adjuster", description="Unique conversation thread ID")


class ChatResetRequest(BaseModel):
    session_id: Optional[str] = Field("default_adjuster", description="Session ID to clear")


class ChatMessageResponse(BaseModel):
    reply: str
    tools_called: List[str]
    referenced_claims: List[str]
    session_id: str


@chat_router.post(
    "/message",
    response_model=ChatMessageResponse,
    summary="Process Natural Language Adjuster Query"
)
def send_chat_message(req: ChatMessageRequest):
    """Processes an adjuster's natural language question through the tool-equipped LLM agent."""
    try:
        result = process_chat_message(user_message=req.message, session_id=req.session_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat processing failed: {str(e)}"
        )


@chat_router.post("/reset", summary="Clear Session Memory")
def clear_chat_history(req: ChatResetRequest):
    """Clears conversation context for the specified session ID."""
    reset_session(req.session_id)
    return {"success": True, "message": f"Session '{req.session_id}' cleared."}


@chat_router.get("/suggestions", summary="Get Quick Starter Prompts")
def get_prompt_suggestions():
    """Returns curated starter prompts for adjusters."""
    return {
        "suggestions": [
            {
                "category": "High Risk & Anomaly",
                "prompt": "Show me the top 5 highest risk claims currently pending review."
            },
            {
                "category": "Reporting Delays",
                "prompt": "Which claims have a reporting delay over 30 days and no police report?"
            },
            {
                "category": "Semantic Incident Match",
                "prompt": "Find previous claims involving water leakage while the homeowner was on vacation."
            },
            {
                "category": "Portfolio KPIs",
                "prompt": "What is our overall claim approval rate, SIU escalation rate, and total claims count?"
            },
            {
                "category": "Claim Deep-Dive",
                "prompt": "Why was claim CLM_DIRTY_002 escalated to SIU? Summarize key forensic flags."
            }
        ]
    }
