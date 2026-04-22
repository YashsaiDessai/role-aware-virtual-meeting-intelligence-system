"""
Pydantic models for structured meeting intelligence output.
Enforces strict schema validation for Ollama JSON-mode responses.
"""

from enum import Enum
from typing import List, Optional

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
    deadline: Optional[str] = Field(
        default=None,
        description="Deadline or timeframe if mentioned, e.g. 'by Thursday', 'this sprint'",
    )


class MeetingOutput(BaseModel):
    """
    Top-level structured output from the meeting analysis pipeline.
    """
    summary: str = Field(
        ...,
        description="Concise role-tailored executive summary of the meeting (3-5 sentences)",
    )
    key_themes: List[str] = Field(
        default_factory=list,
        description="2-5 high-level themes or topics discussed in the meeting",
    )
    decisions: List[str] = Field(
        ...,
        description="Key decisions made during the meeting",
    )
    action_items: List[ActionItem] = Field(
        ...,
        description="Concrete next-step tasks with owners and priorities",
    )
    risks: List[str] = Field(
        default_factory=list,
        description="Risks, blockers, or escalation points mentioned",
    )
