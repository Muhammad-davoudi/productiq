import uuid
from typing import Optional
from fastapi import APIRouter, Header, Depends
from pydantic import BaseModel

from src.llm.service import AssistantService

router = APIRouter(prefix="/api")


class UserQueryRequest(BaseModel):
    query: str


def get_assistant_service() -> AssistantService:
    return AssistantService()


@router.post("/assistant/recommend")
def get_assistant_recommendation(
    payload: UserQueryRequest,
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID"),
    service: AssistantService = Depends(get_assistant_service)
):
    session_id = x_session_id or str(uuid.uuid4())
    reply_content = service.process_input(session_id=session_id, user_input=payload.query)
    
    return {
        "status": "success",
        "reply": reply_content,
        "session_id": session_id
    }
