"""Critic Agent Core: Evaluates Harvard CV and STAR bullets across 4 rigorous dimensions:
1. Quantifiable Metrics (0-25 pts)
2. Anti-Hallucination & Grounding (0-25 pts)
3. ATS Keyword Alignment (0-25 pts)
4. Harvard Action Verbs & Brevity (0-25 pts)
"""

import re
from typing import Any
from ai.models.candidate import CandidateProfile
from ai.models.critic import CriticEvaluationReport
from ai.models.harvard_cv import HarvardCVData


# High-impact Harvard Action Verbs in English & Vietnamese
HARVARD_ACTION_VERBS = {
    # English Action Verbs
    "architected", "engineered", "spearheaded", "designed", "developed", "built",
    "implemented", "optimized", "scaled", "automated", "streamlined", "reduced",
    "increased", "accelerated", "deployed", "refactored", "orchestrated", "migrated",
    "integrated", "authored", "led", "mentored", "established", "formulated",
    "boosted", "delivered", "transformed", "eliminated", "standardized",
    # Vietnamese Action Verbs
    "thiết kế", "xây dựng", "phát triển", "tối ưu", "tối ưu hóa", "tự động hóa",
    "triển khai", "nâng cấp", "cắt giảm", "tăng trưởng", "dẫn dắt", "tái cấu trúc",
    "tích hợp", "tiên phong", "chuẩn hóa", "chuyển đổi", "hoàn thành", "áp dụng",
}

# Weak passive filler phrases to penalize
WEAK_FILLER_PHRASES = [
    "chịu trách nhiệm", "tham gia vào", "hỗ trợ việc", "làm việc với",
    "responsible for", "participated in", "helped with", "worked on", "assisted in",
    "tasked with", "handled duties",
]

# Regex pattern for numerical and quantifiable achievements
METRIC_REGEX = re.compile(
    r"(\d+(\.\d+)?%|\$\d+(,\d+)*|\b\d+(k|m|b|\+)?\b|\b\d+x\b|\b\d+\s*(ms|giây|phút|giờ|người|users|rps|tps|request|dự án|kỹ sư|thành viên|lần|đoàn|khách hàng|vnds?|triệu|tỷ)\b)",
    re.IGNORECASE,
)


class CriticAgent:
    """Independent Audit Agent that inspects synthesized CVs with zero tolerance for fluff."""

    def __init__(self, approval_threshold: int = 90):
        self.approval_threshold = approval_threshold

    def evaluate(
        self,
        cv_data: HarvardCVData,
        raw_profile: CandidateProfile | None = None,
        target_jd_text: str | None = None,
        iteration: int = 1,
    ) -> CriticEvaluationReport:
        """Run full 4-dimension audit on a synthesized Harvard CV."""
        feedback_list: list[str] = []
        hallucinations: list[str] = []
        improvements: list[str] = []
        dim_scores: dict[str, int] = {}

        # Collect all bullet points from experience and projects
        all_bullets: list[str] = []
        for exp in cv_data.experience:
            all_bullets.extend(exp.bullets)
        for proj in cv_data.projects:
            all_bullets.extend(proj.bullets)

        total_bullets = max(len(all_bullets), 1)

        # ── 1. Quantifiable Metrics Evaluation (0-25 pts) ───────────────
        metric_bullets = [b for b in all_bullets if METRIC_REGEX.search(b)]
        metric_ratio = len(metric_bullets) / total_bullets

        if metric_ratio >= 0.8:
            metrics_score = 25
        elif metric_ratio >= 0.6:
            metrics_score = 20
            improvements.append("Bổ sung thêm số liệu định lượng (%, ms, DAU, quy mô) cho ít nhất 2 câu kinh nghiệm còn lại.")
        elif metric_ratio >= 0.4:
            metrics_score = 15
            feedback_list.append("Nhiều câu kinh nghiệm còn thiếu số liệu đo lường thành tựu định lượng.")
            improvements.append("Cần đưa các con số cụ thể về hiệu năng, tỷ lệ tăng trưởng hoặc quy mô tải vào các câu đạn.")
        else:
            metrics_score = 8
            feedback_list.append("Nghiêm trọng: Đa số các câu bullet point chỉ mô tả nhiệm vụ chung chung mà không có số liệu định lượng.")
            improvements.append("Bắt buộc thêm con số định lượng (%) vào từng câu đạn theo chuẩn STAR.")

        dim_scores["quantifiable_metrics"] = metrics_score

        # ── 2. Anti-Hallucination & Contextual Grounding (0-25 pts) ─────
        hallucination_score = 25
        if raw_profile:
            # Extract known skills from raw profile
            known_skills = set()
            for group in raw_profile.skills_taxonomy.model_dump().values():
                if isinstance(group, list):
                    for s in group:
                        s_name = s.get("name", "") if isinstance(s, dict) else str(s)
                        if s_name:
                            known_skills.add(s_name.lower())

            # Check if any new skill in cv_data was completely fabricated
            synthesized_skills = set()
            for cat in cv_data.skills_categories:
                for sk in cat.skills:
                    synthesized_skills.add(sk.lower())

            # Known background context
            known_context_blob = (
                f"{raw_profile.personal_info.full_name} "
                f"{raw_profile.summary.summary_text or ''} "
                f"{' '.join(known_skills)}"
            ).lower()

            for exp in raw_profile.work_experience:
                known_context_blob += f" {exp.company} {exp.role} {' '.join(exp.raw_bullets)}".lower()

            for proj in raw_profile.projects:
                known_context_blob += f" {proj.name} {proj.description} {' '.join(proj.technologies)}".lower()

            # Identify potentially hallucinated words in technical skills
            for sk in synthesized_skills:
                if len(sk) > 3 and sk not in known_context_blob and sk not in known_skills:
                    # If target JD provided, check if it was just injected from JD without candidate context
                    if target_jd_text and sk in target_jd_text.lower():
                        hallucinations.append(f"Kỹ năng '{sk}' xuất hiện trong JD nhưng không có chứng cứ trong CV gốc của ứng viên.")
                        hallucination_score -= 5

        hallucination_score = max(hallucination_score, 5)
        if hallucinations:
            feedback_list.append(f"Phát hiện {len(hallucinations)} điểm chưa được kiểm chứng từ CV gốc.")
            improvements.append("Loại bỏ hoặc chỉ định rõ các kỹ năng chưa có chứng cứ trong kinh nghiệm làm việc thực tế.")

        dim_scores["anti_hallucination"] = hallucination_score

        # ── 3. ATS Keyword Alignment (0-25 pts) ─────────────────────────
        ats_score = 22  # Base solid score
        if cv_data.skills_categories:
            total_skills = sum(len(c.skills) for c in cv_data.skills_categories)
            if 8 <= total_skills <= 18:
                ats_score = 25
            elif total_skills > 20:
                ats_score = 16
                feedback_list.append("Cảnh báo: Danh sách kỹ năng quá dài (>20 skills), có dấu hiệu nhồi từ khóa (Keyword Stuffing).")
                improvements.append("Cắt giảm danh sách kỹ năng về chuẩn 10-15 kỹ năng tinh hoa nhất của vị trí.")
            else:
                ats_score = 18
                improvements.append("Bổ sung đầy đủ 10-15 kỹ năng cốt lõi theo 3 nhóm chuyên môn.")
        else:
            ats_score = 10
            feedback_list.append("Thiếu phần Skills Categories chuẩn hóa.")

        dim_scores["ats_alignment"] = ats_score

        # ── 4. Harvard Action Verbs & Brevity (0-25 pts) ─────────────────
        verb_score = 25
        passive_count = 0
        weak_starts = 0

        for b in all_bullets:
            b_lower = b.strip().lower()
            # Check for passive filler
            if any(filler in b_lower for filler in WEAK_FILLER_PHRASES):
                passive_count += 1

            # Check starting word, stripping any leading bullet symbols or punctuation
            clean_line = b_lower.lstrip("•-*·–— \t")
            first_word = clean_line.split()[0] if clean_line else ""
            first_two = " ".join(clean_line.split()[:2]) if len(clean_line.split()) >= 2 else first_word
            if first_word not in HARVARD_ACTION_VERBS and first_two not in HARVARD_ACTION_VERBS:
                weak_starts += 1

        if passive_count > 0:
            verb_score -= min(passive_count * 4, 10)
            feedback_list.append(f"Có {passive_count} câu dùng từ ngữ thụ động ('chịu trách nhiệm', 'tham gia vào').")
            improvements.append("Thay thế các cụm từ thụ động bằng động từ hành động dứt khoát (Thiết kế, Tối ưu, Xây dựng, Spearheaded).")

        if weak_starts > total_bullets * 0.4:
            verb_score -= 5
            improvements.append("Đảm bảo 100% câu bullet point bắt đầu trực tiếp bằng Action Verb quá khứ.")

        verb_score = max(verb_score, 10)
        dim_scores["action_verbs_brevity"] = verb_score

        # ── Final Score & Approval ──────────────────────────────────────
        total_score = sum(dim_scores.values())
        is_approved = (total_score >= self.approval_threshold) and (len(hallucinations) == 0)

        return CriticEvaluationReport(
            total_score=total_score,
            is_approved=is_approved,
            dimension_scores=dim_scores,
            critique_feedback=feedback_list,
            flagged_hallucinations=hallucinations,
            actionable_improvements=improvements,
            evaluated_at_step=iteration,
        )
