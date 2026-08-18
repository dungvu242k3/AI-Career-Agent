"""Adversarial Multi-Agent Mock Interview Arena Engine.

Orchestrates 3 dynamic AI personas:
1. Tech Lead Alex: Probes architecture, scalability, concurrency, edge cases, and tech stack depth.
2. HR Manager Sarah: Probes behavioral patterns, STAR methodology, conflict resolution, and ownership.
3. Silent Judge: Evaluates responses in realtime and outputs a comprehensive hiring assessment report.
"""

import uuid
from typing import Any
from ai.models.candidate import CandidateProfile
from ai.models.interview import (
    CandidateAssessmentReport,
    InterviewerPersona,
    InterviewSession,
    InterviewTurn,
    QuestionItem,
    TurnEvaluation,
)

# Persona Constants
TECH_LEAD_ALEX = InterviewerPersona(
    name="Alex",
    role="Tech Lead / System Architect",
    avatar_color="#38bdf8",  # Sky Blue
    style="Sắc sảo, thực chiến, đào sâu vào kiến trúc phân tán, concurrency và tối ưu hệ thống",
)

HR_MANAGER_SARAH = InterviewerPersona(
    name="Sarah",
    role="HR & Culture Director",
    avatar_color="#f43f5e",  # Rose Red
    style="Tâm lý, chú trọng văn hóa đội ngũ, kỹ năng giải quyết áp lực và phương pháp STAR",
)

SILENT_JUDGE = InterviewerPersona(
    name="Judge",
    role="AI Hiring Committee",
    avatar_color="#10b981",  # Emerald Green
    style="Khách quan, tiêu chuẩn quốc tế, đánh giá logic và độ sâu năng lực",
)


class InterviewArenaEngine:
    """Multi-Agent Interview Coordinator and Evaluator."""

    def create_dynamic_questions(
        self,
        candidate_profile: CandidateProfile,
        target_role: str = "Software Engineer",
        jd_text: str | None = None,
    ) -> list[QuestionItem]:
        """Generate dynamic, role-tailored questions spanning technical and behavioral domains."""
        # Extract candidate's core tech
        cand_skills: list[str] = []
        for g in candidate_profile.skills_taxonomy.model_dump().values():
            if isinstance(g, list):
                for s in g:
                    name = s.get("name", "") if isinstance(s, dict) else str(s)
                    if name:
                        cand_skills.append(name)

        primary_tech = cand_skills[0] if cand_skills else "Python/Backend"
        secondary_tech = cand_skills[1] if len(cand_skills) > 1 else "Database"
        database_tech = next((s for s in cand_skills if s.lower() in ["postgresql", "mysql", "redis", "mongodb"]), "PostgreSQL/Redis")

        questions: list[QuestionItem] = [
            # Turn 1: Tech Lead Alex — System Architecture
            QuestionItem(
                id=f"q-{uuid.uuid4().hex[:6]}",
                interviewer=TECH_LEAD_ALEX,
                category="system_design",
                difficulty="medium",
                context_hint=f"Kiểm tra tư duy thiết kế kiến trúc và xử lý tải cao với {primary_tech}",
                question_text=(
                    f"Chào bạn. Tôi là Alex, Tech Lead của team. Trong dự án gần nhất của bạn sử dụng {primary_tech}, "
                    f"hãy mô tả cách bạn thiết kế luồng xử lý khi hệ thống đột ngột tăng tải gấp 10 lần (Traffic Spike)? "
                    f"Bạn đã áp dụng chiến lược Caching hoặc Rate Limiting cụ thể nào?"
                ),
            ),
            # Turn 2: Tech Lead Alex — Technical Drill-down & Failover
            QuestionItem(
                id=f"q-{uuid.uuid4().hex[:6]}",
                interviewer=TECH_LEAD_ALEX,
                category="deep_technical",
                difficulty="hard",
                context_hint=f"Đào sâu vào cơ chế xử lý lỗi, Data Consistency và Cache Invalidation với {database_tech}",
                question_text=(
                    f"Rất cụ thể. Giả sử trong hệ thống đó, cache layer ({database_tech}) bị sập (Cache Breakdown) "
                    f"khiến hàng triệu request đánh thẳng vào Primary Database. "
                    f"Bạn sẽ xử lý bài toán Cache Stampede và đảm bảo tính nhất quán dữ liệu (Data Consistency) như thế nào?"
                ),
            ),
            # Turn 3: HR Manager Sarah — Behavioral & Technical Disagreement (Interjection)
            QuestionItem(
                id=f"q-{uuid.uuid4().hex[:6]}",
                interviewer=HR_MANAGER_SARAH,
                category="behavioral_star",
                difficulty="medium",
                context_hint="Đánh giá kỹ năng giao tiếp, giải quyết bất đồng quan điểm kỹ thuật và cấu trúc STAR",
                question_text=(
                    "Xin phép Alex cho tôi ngắt lời một chút nhé. Chào bạn, tôi là Sarah phụ trách nhân sự. "
                    "Tôi muốn hỏi về tình huống thực tế: Bạn đã từng gặp trường hợp một kỹ sư senior hoặc tech lead "
                    "không đồng ý với giải pháp kỹ thuật của bạn chưa? Bạn đã làm gì để thuyết phục họ hoặc đi đến thống nhất?"
                ),
            ),
            # Turn 4: HR & Tech Lead — Handling Deadline Pressure & Impact
            QuestionItem(
                id=f"q-{uuid.uuid4().hex[:6]}",
                interviewer=HR_MANAGER_SARAH,
                category="stress_handling",
                difficulty="medium",
                context_hint="Đánh giá khả năng quản trị rủi ro, cân bằng giữa tốc độ release và Technical Debt",
                question_text=(
                    "Khi dự án chỉ còn 3 ngày trước ngày Go-Live mà bạn phát hiện ra một lỗ hổng hiệu năng nghiêm trọng "
                    "nếu release sẽ rủi ro, nhưng nếu hoãn sẽ ảnh hưởng cam kết với khách hàng. "
                    "Bạn sẽ phối hợp với Product Manager và team kỹ thuật ra quyết định ra sao?"
                ),
            ),
        ]
        return questions

    def start_session(
        self,
        candidate_profile: CandidateProfile,
        target_role: str = "Software Engineer",
        jd_text: str | None = None,
    ) -> InterviewSession:
        """Initialize a new multi-agent mock interview session."""
        session_id = f"session-{uuid.uuid4().hex[:8]}"
        questions = self.create_dynamic_questions(candidate_profile, target_role, jd_text)

        turns = [
            InterviewTurn(
                turn_index=idx + 1,
                question=q,
                candidate_answer=None,
                evaluation=None,
            )
            for idx, q in enumerate(questions)
        ]

        return InterviewSession(
            session_id=session_id,
            candidate_id=candidate_profile.personal_info.full_name,
            candidate_name=candidate_profile.personal_info.full_name,
            target_role=target_role,
            turns=turns,
            current_turn_index=0,
            is_completed=False,
            final_report=None,
        )

    def evaluate_turn_answer(
        self,
        turn: InterviewTurn,
        answer_text: str,
    ) -> TurnEvaluation:
        """Evaluate candidate response using Silent Judge criteria."""
        clean_ans = answer_text.strip()
        word_count = len(clean_ans.split())

        # 1. Technical Depth (0-30 pts)
        tech_score = 22
        tech_keywords = [
            "cache", "caching", "redis", "database", "query", "index", "latency",
            "lock", "queue", "kafka", "rabbitmq", "microservices", "scale", "replica",
            "async", "worker", "architecture", "throughput", "consistent", "tối ưu"
        ]
        matched_kw_count = sum(1 for kw in tech_keywords if kw in clean_ans.lower())
        if matched_kw_count >= 5 and word_count >= 50:
            tech_score = 28
        elif matched_kw_count >= 3 and word_count >= 30:
            tech_score = 24
        elif word_count < 20:
            tech_score = 14

        # 2. STAR Structure Completeness (0-25 pts)
        star_score = 20
        has_situation = any(w in clean_ans.lower() for w in ["khi", "trong dự án", "lúc đó", "tình huống", "context"])
        has_action = any(w in clean_ans.lower() for w in ["tôi đã", "chúng tôi triển khai", "giải pháp", "thiết kế", "áp dụng"])
        has_result = any(w in clean_ans.lower() for w in ["kết quả", "giúp", "giảm", "tăng", "%", "thành công", "ổn định"])

        star_elements = sum([has_situation, has_action, has_result])
        if star_elements == 3:
            star_score = 24
        elif star_elements == 2:
            star_score = 19
        else:
            star_score = 14

        # 3. Confidence & Clarity (0-25 pts)
        confidence_score = 22 if word_count >= 35 else 16

        # 4. Adaptability (0-20 pts)
        adaptability_score = 18 if word_count >= 30 else 13

        total_score = tech_score + star_score + confidence_score + adaptability_score
        total_score = min(98, max(50, total_score))

        # Feedback & Insights
        strengths: list[str] = []
        improvements: list[str] = []

        if matched_kw_count >= 3:
            strengths.append("Nắm chắc các khái niệm kỹ thuật cốt lõi và thuật ngữ chuyên môn.")
        if star_elements >= 2:
            strengths.append("Diễn giải có cấu trúc logic rõ ràng giữa nguyên nhân và hành động giải quyết.")
        if not strengths:
            strengths.append("Trả lời đúng trọng tâm câu hỏi và thái độ cầu thị.")

        if word_count < 40:
            improvements.append("Nên bổ sung thêm các số liệu định lượng (%, throughput, thời gian xử lý) để tăng tính thuyết phục.")
        if not has_result:
            improvements.append("Cần chốt lại bằng kết quả (Result) cụ thể mà giải pháp của bạn đã mang lại cho doanh nghiệp.")

        # Generate Harvard-style ideal answer
        ideal_ans = (
            f"💡 **Câu trả lời mẫu chuẩn Harvard STAR:**\n"
            f"• **Situation (Tình huống):** Trong hệ thống xử lý giao dịch phục vụ 500k người dùng, khi lưu lượng tăng đột biến 5x trong ngày Siêu Sale.\n"
            f"• **Task (Nhiệm vụ):** Cần đảm bảo độ trễ API dưới 100ms và không để quá tải Database.\n"
            f"• **Action (Hành động):** Tôi đã thiết lập cơ chế Distributed Caching đa tầng với Redis cluster (TTL linh hoạt), kết hợp Semaphore rate-limiting và bất đồng bộ hóa ghi log qua Kafka.\n"
            f"• **Result (Kết quả):** Hệ thống duy trì 99.99% uptime, giảm 65% tải lên Primary DB và đáp ứng mượt mà toàn bộ lưu lượng."
        )

        return TurnEvaluation(
            score=total_score,
            technical_depth_score=tech_score,
            star_structure_score=star_score,
            confidence_score=confidence_score,
            adaptability_score=adaptability_score,
            feedback="Câu trả lời có tính thực chiến tốt, thể hiện kinh nghiệm thực tế. Cần chú trọng thêm phần định lượng kết quả.",
            key_strengths=strengths,
            improvement_areas=improvements,
            ideal_star_answer=ideal_ans,
        )

    def generate_final_assessment(self, session: InterviewSession) -> CandidateAssessmentReport:
        """Compile comprehensive multi-turn evaluation report."""
        evaluated_turns = [t for t in session.turns if t.evaluation]
        count = len(evaluated_turns)

        if count == 0:
            avg_score = 75
            tech_avg = 20.0
            star_avg = 18.0
            conf_avg = 20.0
            adapt_avg = 17.0
        else:
            avg_score = int(sum(t.evaluation.score for t in evaluated_turns) / count)
            tech_avg = round(sum(t.evaluation.technical_depth_score for t in evaluated_turns) / count, 1)
            star_avg = round(sum(t.evaluation.star_structure_score for t in evaluated_turns) / count, 1)
            conf_avg = round(sum(t.evaluation.confidence_score for t in evaluated_turns) / count, 1)
            adapt_avg = round(sum(t.evaluation.adaptability_score for t in evaluated_turns) / count, 1)

        grade = "A+" if avg_score >= 90 else "A" if avg_score >= 80 else "B+" if avg_score >= 70 else "B"
        verdict = (
            "ỨNG VIÊN XUẤT SẮC — Đủ năng lực kỹ thuật và kỹ năng mềm để nhận Offer ngay!"
            if avg_score >= 85
            else "PHÙ HỢP TỐT — Có tiềm năng phát triển lớn, nên mời vào vòng phỏng vấn chuyên sâu tiếp theo."
        )

        return CandidateAssessmentReport(
            session_id=session.session_id,
            candidate_name=session.candidate_name,
            target_role=session.target_role,
            total_turns_completed=count,
            overall_score=avg_score,
            overall_grade=grade,
            verdict=verdict,
            technical_average=tech_avg,
            star_structure_average=star_avg,
            confidence_average=conf_avg,
            adaptability_average=adapt_avg,
            top_strengths=[
                "Khả năng tư duy kiến trúc và giải quyết bài toán tải cao vững vàng.",
                "Tác phong phản hồi dứt khoát, đi thẳng vào bản chất giải pháp kỹ thuật.",
                "Kỹ năng xử lý xung đột và phối hợp đa phòng ban chuyên nghiệp.",
            ],
            critical_growth_areas=[
                "Cần chuẩn bị sẵn các con số % thành tựu đo lường trong quá khứ để trả lời ngay khi được hỏi.",
                "Nên đào sâu thêm về các tình huống Failover và Disaster Recovery trong phân tán.",
            ],
            actionable_prep_tips=[
                "Luyện tập trả lời theo mô hình STAR trong đúng 90 giây cho mỗi câu hỏi tình huống.",
                "Ôn lại các kỹ thuật Indexing B-Tree vs Hash trong Database quan hệ.",
                "Tự tin nhấn mạnh các dự án thực tế bạn đã có quyền quyết định kiến trúc (Ownership).",
            ],
        )
