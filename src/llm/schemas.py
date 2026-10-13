from pydantic import BaseModel
from typing import List, Optional

class ExtractedIntent(BaseModel):
    intent: str
    keywords: List[str]
    emotion: str
    out_of_scope_query: bool = False
    needs_clarification: bool = False

class AssistantResponse(BaseModel):
    response_text: str
    extracted_intent: ExtractedIntent
    grounded_products: List[dict] = []
    session_ended: bool = False
