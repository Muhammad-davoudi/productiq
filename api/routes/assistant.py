import uuid
from fastapi import APIRouter, Header, Depends
from pydantic import BaseModel
from typing import Optional
from src.llm.service import AssistantService

router = APIRouter()

class UserQueryRequest(BaseModel):
    query: str

def get_assistant_service():
    return AssistantService()

@router.post("/assistant/recommend")
def get_assistant_recommendation(
    payload: UserQueryRequest,
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID"),
    service: AssistantService = Depends(get_assistant_service)
):
    session_id = x_session_id or str(uuid.uuid4())
    result = service.handle_message(session_id=session_id, user_input=payload.query)
    return {
        "status": result["status"],
        "reply": result["response"],
        "session_id": session_id
    }
