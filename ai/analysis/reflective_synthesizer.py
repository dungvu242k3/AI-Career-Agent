"""Grounded CV synthesis with deterministic critic/reflection diagnostics."""

from __future__ import annotations

import copy
import logging
from typing import Literal

from ai.analysis.critic_agent import CriticAgent, WEAK_FILLER_PHRASES
from ai.analysis.harvard_synthesizer import HarvardCVSynthesizer
from ai.grounding import ground_cv_for_export
from ai.models.candidate import CandidateProfile
from ai.models.critic import CriticEvaluationReport, ReflectiveSynthesisResult
from ai.models.harvard_cv import HarvardCVData
from ai.models.jd import JDMatchReport, JDProfile


logger = logging.getLogger(__name__)


class ReflectiveHarvardSynthesizer:
    """Actor/critic loop that never invents quantified achievements."""

    def __init__(
        self,
        approval_threshold: int = 90,
        max_iterations: int = 3,
        ai_provider: Literal["openai", "gemini"] | None = None,
    ):
        self.max_iterations = max_iterations
        self.actor_synthesizer = HarvardCVSynthesizer(ai_provider=ai_provider)
        self.critic_agent = CriticAgent(approval_threshold=approval_threshold)

    def _refine_draft_with_feedback(
        self,
        cv_draft: HarvardCVData,
        critic_report: CriticEvaluationReport,
        profile: CandidateProfile,
    ) -> HarvardCVData:
        """Improve wording only; never manufacture metrics or claims."""
        refined = copy.deepcopy(cv_draft)
        for experience in refined.experience:
            improved: list[str] = []
            for bullet in experience.bullets:
                text = bullet.strip()
                for weak in WEAK_FILLER_PHRASES:
                    if text.lower().startswith(weak):
                        text = text[len(weak):].strip()
                        break
                improved.append(text)
            experience.bullets = improved

        if critic_report.flagged_hallucinations:
            for category in refined.skills_categories:
                category.skills = [
                    skill
                    for skill in category.skills
                    if not any(skill.lower() in finding.lower() for finding in critic_report.flagged_hallucinations)
                ]
        return refined

    async def synthesize(
        self,
        profile: CandidateProfile,
        jd: JDProfile,
        report: JDMatchReport,
        target_language: Literal["en", "vi"] = "vi",
    ) -> tuple[HarvardCVData, ReflectiveSynthesisResult]:
        current = await self.actor_synthesizer.synthesize(profile, jd, report, target_language)
        best_cv = current
        best_report: CriticEvaluationReport | None = None
        history: list[dict] = []

        for iteration in range(1, self.max_iterations + 1):
            critic = self.critic_agent.evaluate(current, profile, jd.raw_text, iteration)
            history.append(
                {
                    "iteration": iteration,
                    "score": critic.total_score,
                    "dimension_scores": critic.dimension_scores,
                    "feedback": critic.critique_feedback,
                    "approved": critic.is_approved,
                }
            )
            if best_report is None or critic.total_score > best_report.total_score:
                best_cv, best_report = current, critic
            if critic.is_approved or iteration == self.max_iterations:
                break
            current = self._refine_draft_with_feedback(current, critic, profile)

        assert best_report is not None
        grounded_cv, grounding = ground_cv_for_export(best_cv, profile, report)
        synthesis = ReflectiveSynthesisResult(
            is_converged=best_report.is_approved,
            iterations_count=len(history),
            final_critic_score=best_report.total_score,
            critic_report=best_report,
            reflection_history=history,
            grounding_report={
                "is_grounded": grounding.is_grounded,
                "dropped_claims": grounding.dropped_claims,
                "verified_skills": grounding.verified_skills,
                "verified_certifications": grounding.verified_certifications,
            },
        )
        return grounded_cv, synthesis
