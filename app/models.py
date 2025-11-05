"""
Pydantic models for API requests and responses.
"""
from pydantic import BaseModel, Field
from typing import Dict


class TextAnalysisRequest(BaseModel):
    """Request model for text analysis."""
    text: str = Field(..., min_length=1, max_length=10000, description="Text to analyze for toxicity")


class TextAnalysisResponse(BaseModel):
    """Response model for text analysis."""
    text_id: str = Field(..., description="Anonymized text identifier (GDPR compliant)")
    score: float = Field(..., ge=0, le=100, description="Toxicity score from 0 (safe) to 100 (toxic)")
    toxic: bool = Field(..., description="Whether the text is considered toxic")
    categories: Dict[str, float] = Field(..., description="Toxicity categories with scores")


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str = Field(..., description="Health status")
    model_loaded: bool = Field(..., description="Whether the ML model is loaded")
