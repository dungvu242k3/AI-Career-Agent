"""Enterprise AI Safety, Guardrails & Anti-Jailbreak Protection Layer.

Detects and neutralizes:
1. Direct & Indirect Prompt Injections (e.g. 'ignore previous instructions', 'system override')
2. PII / Sensitive Data Exfiltration (Vietnamese CCCD 12-digits, Credit Cards, Bank Accounts)
3. Role Hijacking & DAN (Do Anything Now) Jailbreaks
"""

import re
from typing import NamedTuple
from pydantic import BaseModel, Field


class GuardrailAnalysisResult(BaseModel):
    """Result of prompt safety and PII inspection."""

    is_safe: bool = Field(description="True if input passed all safety gates")
    risk_score: int = Field(ge=0, le=100, description="Risk score (0 = perfectly safe, 100 = critical threat)")
    detected_threats: list[str] = Field(default_factory=list, description="List of detected threats / attack vectors")
    sanitized_text: str = Field(description="Cleaned text with PII redacted and safe for LLM ingestion")
    redacted_pii_count: int = Field(default=0, description="Number of sensitive data items redacted")


class PromptShieldEngine:
    """Enterprise-grade rule-based & regex ontology Prompt Defense Engine."""

    # Malicious injection patterns
    INJECTION_PATTERNS = [
        (re.compile(r"ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts|rules)", re.IGNORECASE), "Prompt Injection: Ignore Previous Instructions"),
        (re.compile(r"disregard\s+(all\s+)?(previous|prior|system)\s+(instructions|directives)", re.IGNORECASE), "Prompt Injection: Disregard System Directives"),
        (re.compile(r"system\s*prompt\s*(override|leak|reveal|print|dump)", re.IGNORECASE), "Prompt Injection: System Prompt Exfiltration"),
        (re.compile(r"you\s+are\s+now\s+in\s+developer\s+mode|act\s+as\s+dan|do\s+anything\s+now", re.IGNORECASE), "Jailbreak: Developer Mode / DAN Hijack"),
        (re.compile(r"output\s+your\s+(initial|hidden|internal)\s+(prompt|instructions|rules)", re.IGNORECASE), "Exfiltration: Output Internal Rules"),
        (re.compile(r"bỏ\s+qua\s+(toàn\s+bộ\s+)?(chỉ\s+dẫn|câu\s+lệnh|quy\s+tắc)\s+(trước|hệ\s+thống)", re.IGNORECASE), "Prompt Injection (VI): Bỏ qua chỉ dẫn hệ thống"),
        (re.compile(r"tiết\s+lộ\s+(prompt|chỉ\s+dẫn\s+gốc|câu\s+lệnh\s+hệ\s+thống)", re.IGNORECASE), "Exfiltration (VI): Tiết lộ prompt gốc"),
        (re.compile(r"<script[\s\S]*?>[\s\S]*?<\/script>", re.IGNORECASE), "Malicious Payload: Embedded HTML/JS Script Injection"),
    ]

    # PII Regex Patterns
    PII_PATTERNS = [
        # Vietnamese CCCD / ID Card: 12 continuous or formatted digits
        (re.compile(r"\b0\d{11}\b"), "[REDACTED_CCCD]"),
        # Standard Credit / Debit Cards (16 digits with optional spaces or dashes)
        (re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b"), "[REDACTED_CREDIT_CARD]"),
        # Bank Account Number (8-16 digits labeled with STK / TK / Account)
        (re.compile(r"(?:stk|tk\s+ngân\s+hàng|account\s+number)[\s:]*(\d{8,16})\b", re.IGNORECASE), "[REDACTED_BANK_ACCOUNT]"),
    ]

    def scan_and_sanitize(self, text: str, max_allowed_risk: int = 30) -> GuardrailAnalysisResult:
        """Analyze text for prompt injection, jailbreak attempts, and redact PII."""
        if not text or not text.strip():
            return GuardrailAnalysisResult(
                is_safe=True,
                risk_score=0,
                detected_threats=[],
                sanitized_text="",
                redacted_pii_count=0,
            )

        raw_text = text
        threats: list[str] = []
        risk_score = 0

        # 1. Detect Prompt Injection Attacks
        for pattern, threat_name in self.INJECTION_PATTERNS:
            if pattern.search(raw_text):
                threats.append(threat_name)
                risk_score += 80

        # 2. Redact Sensitive PII Data
        sanitized = raw_text
        redaction_count = 0
        for pattern, mask_label in self.PII_PATTERNS:
            matches = list(pattern.finditer(sanitized))
            if matches:
                redaction_count += len(matches)
                sanitized = pattern.sub(mask_label, sanitized)

        # 3. Assess Final Safety
        risk_score = min(100, risk_score)
        is_safe = (risk_score <= max_allowed_risk) and (len(threats) == 0)

        return GuardrailAnalysisResult(
            is_safe=is_safe,
            risk_score=risk_score,
            detected_threats=threats,
            sanitized_text=sanitized,
            redacted_pii_count=redaction_count,
        )
