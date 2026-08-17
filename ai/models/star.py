"""Canonical domain schemas for STAR bullet point rewriting.

Supports two modes:
1. Missing Skill → Generate STAR-formatted bullet point suggestion
2. Weak Bullet → Rewrite existing bullet point to STAR format
"""

from pydantic import BaseModel, Field


class STARResult(BaseModel):
    """STAR-method rewrite output with two versions for user choice."""

    original: str = Field(description="Original input (skill name or weak bullet)")
    star_v1: str = Field(description="Version 1: Balanced STAR format — clear S-T-A-R structure")
    star_v2: str = Field(description="Version 2: Max Impact — emphasizes metrics and scale")
    action_verb: str = Field(description="Primary power verb used (e.g. Triển khai, Xây dựng)")
    improvements: list[str] = Field(
        default_factory=list,
        description="List of specific improvements made (Vietnamese)",
    )
