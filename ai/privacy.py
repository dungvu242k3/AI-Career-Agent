"""Prompt ingress policy and PII minimisation helpers."""

from __future__ import annotations

import json
import re
from typing import Any

from ai.execution import AIErrorCode, AIExecutionError
from ai.guardrails.prompt_shield import PromptShieldEngine
from ai.models.candidate import CandidateProfile


_shield = PromptShieldEngine()
_EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
_PHONE_RE = re.compile(r"(?<!\d)(?:\+?84|0)(?:[\s.-]?\d){8,10}(?!\d)")
_NAME_LINE_RE = re.compile(r"^[^\d:@/\\]{3,80}$")
_NAME_LABEL_RE = re.compile(
    r"(?im)^\s*(?:full\s+name|name|họ\s*(?:và\s*)?tên)\s*[:\-]\s*([^\n,;]{2,80})"
)
_NAME_HEADERS = {
    "cv", "resume", "curriculum vitae", "personal information", "contact",
    "thong tin ca nhan", "kinh nghiem", "kinh nghiệm", "hoc van", "học vấn",
    "ky nang", "kỹ năng", "experience", "education", "skills", "summary",
}
_DOB_RE = re.compile(r"(?:date\s*of\s*birth|dob|ngày\s*sinh)\s*[:\-]?\s*([^\n,;]+)", re.IGNORECASE)


def sanitize_llm_input(text: str) -> str:
    """Reject prompt injection and return an LLM-safe, PII-reduced string."""
    result = _shield.scan_and_sanitize(text)
    if not result.is_safe:
        raise AIExecutionError(
            AIErrorCode.INPUT_REJECTED,
            "Input was rejected by the AI safety policy",
        )
    return result.sanitized_text


def redact_cv_for_llm(raw_text: str) -> tuple[str, str | None]:
    """Remove direct CV identifiers before extraction while retaining local recovery.

    A name is not reliably identifiable with a global regex, so only a short
    name-like header line is redacted. The original value never leaves this
    process and is restored after the structured extraction completes.
    """
    safe_text = sanitize_llm_input(raw_text)
    labeled_name = _NAME_LABEL_RE.search(safe_text)
    if labeled_name:
        candidate = labeled_name.group(1).strip()
        if _NAME_LINE_RE.fullmatch(candidate):
            return (
                safe_text[:labeled_name.start(1)]
                + "[REDACTED_NAME]"
                + safe_text[labeled_name.end(1):],
                candidate,
            )
    lines = safe_text.splitlines()
    for index, line in enumerate(lines[:8]):
        candidate = line.strip()
        normalized = " ".join(candidate.lower().split())
        tokens = candidate.split()
        if (
            normalized not in _NAME_HEADERS
            and _NAME_LINE_RE.fullmatch(candidate)
            and 2 <= len(tokens) <= 5
            and sum(char.isalpha() for char in candidate) >= 4
        ):
            lines[index] = line.replace(candidate, "[REDACTED_NAME]")
            return "\n".join(lines), candidate
    return safe_text, None


def profile_payload_for_llm(profile: CandidateProfile) -> str:
    """Serialize a candidate without contact identifiers for third-party LLMs."""
    data: dict[str, Any] = profile.model_dump(mode="json")
    personal_info = data.get("personal_info", {})
    personal_info["full_name"] = "Candidate"
    for field in (
        "email", "phone", "location", "date_of_birth", "linkedin_url", "github_url", "portfolio_url"
    ):
        personal_info[field] = None
    data["personal_info"] = personal_info
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def restore_extracted_contact(
    profile: CandidateProfile, original_text: str, full_name: str | None = None
) -> CandidateProfile:
    """Recover only locally parsed contact fields after sending redacted text to AI."""
    email = _EMAIL_RE.search(original_text)
    phone = _PHONE_RE.search(original_text)
    dob = _DOB_RE.search(original_text)
    if email:
        profile.personal_info.email = email.group(0)
    if phone:
        profile.personal_info.phone = re.sub(r"[\s.-]", "", phone.group(0))
    if dob:
        profile.personal_info.date_of_birth = dob.group(1).strip()
    # Only replace the value when the model saw a redaction marker / generic
    # placeholder. This avoids overwriting a valid test-double or a structured
    # result that was populated by an internal, non-LLM extractor.
    generic_names = {"candidate", "[redacted_name]", "ứng viên", "ung vien"}
    if full_name and profile.personal_info.full_name.strip().lower() in generic_names:
        profile.personal_info.full_name = full_name
    return profile
