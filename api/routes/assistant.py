import uuid
from typing import Optional
from fastapi import APIRouter, Header, Depends
from pydantic import BaseModel

from src.llm.service import AssistantService

router = APIRouter()


class UserQueryRequest(BaseModel):
    query: str


def get_assistant_service() -> AssistantService:
    return AssistantService()


@router.post("/assistant/recommend")
def get_assistant_recommendation(
    payload: UserQueryRequest,
    session_id: Optional[str] = Header(None, alias="X-Session-ID"),
    service: AssistantService = Depends(get_assistant_service)
):
    active_session_id = session_id or str(uuid.uuid4())
    result = service.handle_message(session_id=active_session_id, user_input=payload.query)
    return {
        "status": result.get("status", "success"),
        "reply": result.get("response", ""),
        "session_id": active_session_id
    }
