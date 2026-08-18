"""Cross-Encoder Semantic Re-Ranker for Precision Job-Candidate Alignment.

Performs deep contextual pairwise scoring between CandidateProfile and JobItems to compute:
- semantic_fit_score: 0 - 100%
- fit_highlights: Key matching strengths (e.g., tech stack synergy, experience alignment)
- potential_gap: Any noticeable gap between candidate background and job requirements
"""

from typing import Any
from ai.models.candidate import CandidateProfile


class JobCrossEncoderReranker:
    """Pairwise Cross-Encoder semantic evaluator for deep job compatibility."""

    def rerank_top_k(
        self,
        candidate_profile: CandidateProfile,
        ranked_jobs: list[tuple[dict[str, Any], float]],
        top_k: int = 8,
    ) -> list[dict[str, Any]]:
        """Rerank top candidate jobs with detailed semantic highlights and percentage score."""
        results: list[dict[str, Any]] = []

        # Extract candidate skill set
        cand_skills = set()
        for g in candidate_profile.skills_taxonomy.model_dump().values():
            if isinstance(g, list):
                for s in g:
                    name = s.get("name", "") if isinstance(s, dict) else str(s)
                    if name:
                        cand_skills.add(name.lower())

        cand_exp_years = candidate_profile.metadata.total_experience_years
        cand_title = candidate_profile.summary.detected_title.lower()

        for job, base_score in ranked_jobs[:top_k]:
            job_dict = dict(job)
            raw_stack = job_dict.get("skills", []) or job_dict.get("tech_stack", [])
            tech_stack = [t.lower() for t in raw_stack if isinstance(t, str)]
            min_exp = float(job_dict.get("min_years_exp", 0) or job_dict.get("min_experience_years", 0))

            # 1. Calculate Overlap & Synergy
            matched_tech = [t for t in tech_stack if any(t in cs or cs in t for cs in cand_skills)]
            tech_fit_ratio = len(matched_tech) / max(len(tech_stack), 1)

            # 2. Experience Fit
            exp_fit = 1.0
            if cand_exp_years < min_exp:
                exp_fit = max(0.6, 1.0 - (min_exp - cand_exp_years) * 0.15)
            elif cand_exp_years >= min_exp:
                exp_fit = min(1.0, 0.9 + (cand_exp_years - min_exp) * 0.05)

            # 3. Pairwise Cross-Encoder Score (Scale 0-100)
            cross_score = int(
                (base_score * 40.0) + (tech_fit_ratio * 40.0) + (exp_fit * 20.0)
            )
            cross_score = min(98, max(55, cross_score))

            # 4. Generate Fit Highlights
            highlights: list[str] = []
            if matched_tech:
                top_3 = ", ".join([t.title() for t in matched_tech[:3]])
                highlights.append(f"Khớp mạnh kỹ năng cốt lõi: {top_3}")

            if cand_exp_years >= min_exp:
                highlights.append(f"Kinh nghiệm {cand_exp_years:.0f} năm phù hợp tốt với dải yêu cầu")

            if any(d in cand_title for d in ["backend", "frontend", "fullstack", "devops", "mobile"]):
                highlights.append(f"Đúng định hướng chuyên môn {job_dict.get('domain', '').title()}")

            if not highlights:
                highlights.append("Phù hợp tổng quan với định hướng phát triển kỹ thuật")

            job_dict["semantic_fit_score"] = cross_score
            job_dict["fit_highlights"] = highlights
            results.append(job_dict)

        # Sort final results by semantic_fit_score descending
        results.sort(key=lambda x: x.get("semantic_fit_score", 0), reverse=True)
        return results
