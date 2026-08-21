"""STAR rewriter with guardrails and verified-metric enforcement."""

from __future__ import annotations

import json
import re
from typing import Literal

from google.genai import types
from pydantic import ValidationError

from ai.client import get_gemini_client, get_openai_client
from ai.config import get_ai_config
from ai.execution import AIStage, get_ai_executor
from ai.models.star import STARResult
from ai.privacy import sanitize_llm_input
from ai.prompts import load_composed_prompt


_METRIC = re.compile(r"\b\d[\d,]*(?:\.\d+)?\s*(?:%|req/s|rps|tps|ms|seconds?|minutes?|hours?|users?|k|m|x)\b", re.IGNORECASE)
_UNVERIFIED_METRIC_MARKER = "[add verified metric]"


class STARRewriter:
    def __init__(
        self,
        ai_provider: Literal["openai", "gemini"] | None = None,
        enable_fallback: bool | None = None,
    ):
        self.config = get_ai_config()
        self.ai_provider = ai_provider or self.config.ai_provider
        self.enable_fallback = self.config.enable_fallback if enable_fallback is None else enable_fallback
        self.system_instruction = load_composed_prompt("system_prompt.md", "star_rewrite.md")
        self._executor = get_ai_executor()

    @staticmethod
    def _prepare_payload(raw_input: str, target_role: str, context: str | None) -> str:
        payload = f"<target_role>{target_role}</target_role>\n<raw_input>{raw_input}</raw_input>"
        if context and context.strip():
            payload += f"\n<additional_context>{context.strip()}</additional_context>"
        return payload

    async def _rewrite_with_openai(self, raw_input: str, target_role: str, context: str | None) -> STARResult:
        completion = await get_openai_client().beta.chat.completions.parse(
            model=self.config.model_for("analysis", "openai"),
            messages=[
                {"role": "system", "content": self.system_instruction},
                {"role": "user", "content": self._prepare_payload(raw_input, target_role, context)},
            ],
            response_format=STARResult,
            temperature=self.config.reasoning_temperature,
            max_tokens=self.config.reasoning_max_tokens,
        )
        parsed = completion.choices[0].message.parsed
        if not parsed:
            raise ValueError("OpenAI returned no STAR result")
        return parsed

    async def _rewrite_with_gemini(self, raw_input: str, target_role: str, context: str | None) -> STARResult:
        response = await get_gemini_client().aio.models.generate_content(
            model=self.config.model_for("analysis", "gemini"),
            contents=self._prepare_payload(raw_input, target_role, context),
            config=types.GenerateContentConfig(
                system_instruction=self.system_instruction,
                response_mime_type="application/json",
                response_schema=STARResult,
                temperature=self.config.reasoning_temperature,
                max_output_tokens=self.config.reasoning_max_tokens,
            ),
        )
        raw = re.sub(r"^```(?:json)?\n?|\n?```$", "", (response.text or "").strip())
        try:
            return STARResult.model_validate(json.loads(raw))
        except (json.JSONDecodeError, ValidationError) as error:
            raise ValueError("Gemini returned an invalid STAR schema") from error

    @staticmethod
    def _remove_unverified_metrics(result: STARResult, source_text: str) -> STARResult:
        allowed = {match.group(0).lower().replace(" ", "") for match in _METRIC.finditer(source_text)}

        def sanitize(text: str) -> str:
            return _METRIC.sub(
                lambda match: match.group(0) if match.group(0).lower().replace(" ", "") in allowed else _UNVERIFIED_METRIC_MARKER,
                text,
            )

        result.star_v1 = sanitize(result.star_v1)
        result.star_v2 = sanitize(result.star_v2)
        return result

    async def rewrite(
        self, raw_input: str, target_role: str = "Software Engineer", context: str | None = None
    ) -> STARResult:
        raw = raw_input.strip() if raw_input else ""
        if len(raw) < 2:
            raise ValueError("Nội dung đầu vào cần viết lại không được để trống.")
        role = target_role.strip() if target_role and target_role.strip() else "Software Engineer"
        safe_input = sanitize_llm_input(raw)
        safe_context = sanitize_llm_input(context) if context else None
        primary = self._rewrite_with_openai if self.ai_provider == "openai" else self._rewrite_with_gemini
        fallback = self._rewrite_with_gemini if self.ai_provider == "openai" else self._rewrite_with_openai
        outcome = await self._executor.run(
            stage=AIStage.ANALYSIS,
            primary_provider=self.ai_provider,
            primary=lambda: primary(safe_input, role, safe_context),
            fallback_provider=("gemini" if self.ai_provider == "openai" else "openai") if self.enable_fallback else None,
            fallback=(lambda: fallback(safe_input, role, safe_context)) if self.enable_fallback else None,
            input_chars=len(safe_input) + len(safe_context or ""),
            primary_model=self.config.model_for("analysis", self.ai_provider),
            fallback_model=self.config.model_for("analysis", "gemini" if self.ai_provider == "openai" else "openai"),
        )
        result = self._remove_unverified_metrics(outcome.value, f"{raw}\n{context or ''}")
        result.original = raw
        return result


def get_default_star_rewriter() -> STARRewriter:
    return STARRewriter()
