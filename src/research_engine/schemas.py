"""Typed API and report contracts."""

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl, field_validator


class Confidence(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class ResearchRequest(BaseModel):
    query: str = Field(min_length=10, max_length=2000)

    @field_validator("query", mode="before")
    @classmethod
    def trim_query(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value


class LLMReportContent(BaseModel):
    summary: str = Field(min_length=10, max_length=3000)
    recommendation: str = Field(min_length=10, max_length=3000)
    key_factors: list[str] = Field(min_length=2, max_length=6)
    assumptions: list[str] = Field(max_length=6)
    risks: list[str] = Field(max_length=6)
    confidence: Confidence


class ReportSource(BaseModel):
    title: str
    url: HttpUrl


class ResearchReport(BaseModel):
    id: str
    query: str
    summary: str
    recommendation: str
    key_factors: list[str] = Field(min_length=2, max_length=6)
    assumptions: list[str] = Field(max_length=6)
    risks: list[str] = Field(max_length=6)
    confidence: Confidence
    sources: list[ReportSource] = Field(default_factory=list)
    evidence_notice: str
    mode: str
    created_at: datetime


class ReportList(BaseModel):
    reports: list[ResearchReport]
