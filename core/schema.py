"""
Pydantic models for structured meeting intelligence output.
Enforces strict schema validation for Ollama JSON-mode responses.
"""

from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class Priority(str, Enum):
    """Priority levels for action items."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ActionItem(BaseModel):
    """A single actionable task extracted from the meeting."""
    task: str = Field(..., description="Description of the action item")
    owner: str = Field(
        default="Unassigned",
        description="Person responsible. Defaults to 'Unassigned' if not mentioned.",
    )
    priority: Priority = Field(
        default=Priority.MEDIUM,
        description="Urgency level: high, medium, or low",
    )


class MeetingOutput(BaseModel):
    """
    Top-level structured output from the meeting analysis pipeline.
    Every field is required so Pydantic will reject partial LLM responses.
    """
    decisions: List[str] = Field(
        ...,
        description="Key decisions made during the meeting",
    )
    action_items: List[ActionItem] = Field(
        ...,
        description="Concrete next-step tasks with owners and priorities",
    )
    summary: str = Field(
        ...,
        description="Concise role-tailored summary of the meeting",
    )
