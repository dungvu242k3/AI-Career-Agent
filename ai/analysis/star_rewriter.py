"""STAR Bullet Point Rewriter & Generator — Transforms raw/vague bullets or missing skills into STAR format."""

import json
import logging
import re
from typing import Literal
from google.genai import types
from pydantic import ValidationError

from ai.config import get_ai_config
from ai.client import get_openai_client, get_gemini_client
from ai.models.star import STARResult
from ai.prompts import load_composed_prompt

logger = logging.getLogger(__name__)


class STARRewriter:
    """Production AI Rewriter transforming raw CV bullet points or missing skills into STAR format."""

    def __init__(
        self,
        ai_provider: Literal["openai", "gemini"] | None = None,
        enable_fallback: bool | None = None,
    ):
        self.config = get_ai_config()
        self.ai_provider = ai_provider or self.config.ai_provider
        self.enable_fallback = (
            enable_fallback if enable_fallback is not None else self.config.enable_fallback
        )

        self.system_instruction = load_composed_prompt(
            "system_prompt.md",
            "star_rewrite.md",
        )

    def _prepare_payload(self, raw_input: str, target_role: str, context: str | None) -> str:
        """Format inputs into structured XML-wrapped prompt payload."""
        payload = f"<target_role>{target_role}</target_role>\n<raw_input>{raw_input}</raw_input>"
        if context and context.strip():
            payload += f"\n<additional_context>{context.strip()}</additional_context>"
        return payload

    async def _rewrite_with_openai(
        self, raw_input: str, target_role: str, context: str | None
    ) -> STARResult:
        """Rewrite bullet point via OpenAI Structured Outputs."""
        client = get_openai_client()
        user_content = self._prepare_payload(raw_input, target_role, context)

        completion = await client.beta.chat.completions.parse(
            model=self.config.openai_extraction_model,
            messages=[
                {"role": "system", "content": self.system_instruction},
                {"role": "user", "content": user_content},
            ],
            response_format=STARResult,
            temperature=self.config.reasoning_temperature,
            max_tokens=self.config.reasoning_max_tokens,
        )

        parsed_star = completion.choices[0].message.parsed
        if not parsed_star:
            refusal = getattr(completion.choices[0].message, "refusal", None)
            if refusal:
                raise ValueError(f"OpenAI từ chối viết lại STAR: {refusal}")
            raise ValueError("OpenAI trả về phản hồi rỗng khi tạo câu STAR.")

        parsed_star.original = raw_input
        return parsed_star

    async def _rewrite_with_gemini(
        self, raw_input: str, target_role: str, context: str | None
    ) -> STARResult:
        """Rewrite bullet point via Google Gemini response schema."""
        client = get_gemini_client()
        user_content = self._prepare_payload(raw_input, target_role, context)

        response = await client.aio.models.generate_content(
            model=self.config.gemini_flash_lite_model,
            contents=user_content,
            config=types.GenerateContentConfig(
                system_instruction=self.system_instruction,
                response_mime_type="application/json",
                response_schema=STARResult,
                temperature=self.config.reasoning_temperature,
                max_output_tokens=self.config.reasoning_max_tokens,
            ),
        )

        if not response.text:
            raise ValueError("Gemini trả về phản hồi rỗng khi tạo câu STAR.")

        raw_json_str = response.text.strip()
        if raw_json_str.startswith("```"):
            raw_json_str = re.sub(r"^```(?:json)?\n?", "", raw_json_str)
            raw_json_str = re.sub(r"\n?```$", "", raw_json_str)

        try:
            data = json.loads(raw_json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"AI trả về định dạng JSON không hợp lệ: {e}")

        try:
            star = STARResult.model_validate(data)
            star.original = raw_input
            return star
        except ValidationError as e:
            raise ValueError(f"Dữ liệu câu STAR không đúng cấu trúc quy định: {e}")

    async def rewrite(
        self,
        raw_input: str,
        target_role: str = "Software Engineer",
        context: str | None = None,
    ) -> STARResult:
        """Rewrite raw bullet point or missing skill name to high-impact STAR format."""
        cleaned_input = raw_input.strip() if raw_input else ""
        if len(cleaned_input) < 2:
            raise ValueError("Nội dung đầu vào cần viết lại không được để trống.")

        role = target_role.strip() if target_role and target_role.strip() else "Software Engineer"

        primary_fn = (
            self._rewrite_with_openai
            if self.ai_provider == "openai"
            else self._rewrite_with_gemini
        )
        fallback_fn = (
            self._rewrite_with_gemini
            if self.ai_provider == "openai"
            else self._rewrite_with_openai
        )

        try:
            star = await primary_fn(cleaned_input, role, context)
            star.original = cleaned_input
            return star
        except Exception as primary_err:
            if not self.enable_fallback:
                logger.error("Primary STAR rewrite failed: %s", primary_err)
                raise

            logger.warning(
                "Primary STAR rewriter failed: %s. Initiating secondary fallback...",
                primary_err,
            )
            try:
                star = await fallback_fn(cleaned_input, role, context)
                star.original = cleaned_input
                logger.info("Secondary STAR rewriter fallback succeeded.")
                return star
            except Exception as fallback_err:
                logger.error("Both primary and fallback STAR rewriters failed: %s", fallback_err)
                raise ValueError(
                    f"Viết lại STAR thất bại trên cả 2 nhà cung cấp AI: {primary_err} | {fallback_err}"
                )


def get_default_star_rewriter() -> STARRewriter:
    """Factory function for default STARRewriter instance."""
    return STARRewriter()
