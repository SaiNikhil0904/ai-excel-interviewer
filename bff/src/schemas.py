"""
bff/src/schemas.py

Pydantic schemas for validating the BFF's API requests and responses.
"""
from pydantic import BaseModel, Field
from typing import Optional

class ChatMessageInput(BaseModel):
    """Schema for a new message sent by the user."""
    content: str = Field(..., min_length=1, description="The text content of the user's message.")

class ChatMessageOutput(BaseModel):
    """Schema for a message event streamed back to the frontend."""
    type: str = Field(..., description="The type of the event (e.g., 'thought', 'final').")
    content: str = Field(..., description="The text content of the message from the agent.")
    context_id: Optional[str] = Field(None, description="The session/context ID for the conversation.")