"""Adversarial Multi-Agent Mock Interview Arena Engine.

Orchestrates 3 dynamic AI personas:
1. Tech Lead Alex: Probes architecture, scalability, concurrency, edge cases, and tech stack depth.
2. HR Manager Sarah: Probes behavioral patterns, STAR methodology, conflict resolution, and ownership.
3. Silent Judge: Evaluates responses in realtime and outputs a comprehensive hiring assessment report.
"""

import json
import logging
import random
import uuid
import asyncio
from typing import Any, Literal

from ai.client import get_openai_client
from ai.models.candidate import CandidateProfile
from ai.models.interview import (
    CandidateAssessmentReport,
    InterviewerPersona,
    InterviewSession,
    InterviewTurn,
    QuestionItem,
    TurnEvaluation,
)

logger = logging.getLogger(__name__)

# Persona Constants
TECH_LEAD_ALEX = InterviewerPersona(
    name="Alex",
    role="Tech Lead / System Architect",
    avatar_color="#38bdf8",
    style="Sắc sảo, thực chiến, đào sâu vào kiến trúc phân tán, concurrency và tối ưu hệ thống",
)

HR_MANAGER_SARAH = InterviewerPersona(
    name="Sarah",
    role="HR & Culture Director",
    avatar_color="#f43f5e",
    style="Tâm lý, chú trọng văn hóa đội ngũ, kỹ năng giải quyết áp lực và phương pháp STAR",
)

SILENT_JUDGE = InterviewerPersona(
    name="Judge",
    role="AI Hiring Committee",
    avatar_color="#10b981",
    style="Khách quan, tiêu chuẩn quốc tế, đánh giá logic và độ sâu năng lực",
)

SYSTEM_DESIGN_BANK = {
    "backend": "Thiết kế URL Shortener (bit.ly) hoặc Notification System cho 50M user từ đầu.",
    "ai_data": "Thiết kế hệ thống nhận diện khuôn mặt (Face Recognition) real-time hoặc Recommendation Engine.",
    "devops": "Thiết kế CI/CD pipeline cho 200 microservices với Zero-downtime deployment.",
    "mobile": "Thiết kế offline-first sync cho app mobile hoặc hệ thống chat real-time kiểu Zalo.",
    "frontend": "Thiết kế kiến trúc Micro-frontends cho ứng dụng E-commerce khổng lồ.",
}


class InterviewArenaEngine:
    """Multi-Agent Interview Coordinator and Evaluator."""

    async def _enrich_question_with_llm(self, question: QuestionItem, domain: str, skills: str, jd: str) -> QuestionItem:
        client = get_openai_client()
        prompt = f"""
Bạn là {question.interviewer.name}, {question.interviewer.role}. Phong cách: {question.interviewer.style}.
Domain: {domain} | Kỹ năng ứng viên: {skills} | Yêu cầu JD: {jd}
Template gốc: {question.question_text}
Viết lại câu hỏi trên sao cho tự nhiên, mang văn phong giao tiếp, BẮT BUỘC nhắc đến một trong các kỹ năng của ứng viên.
Chỉ trả về nội dung câu hỏi, không giải thích.
"""
        try:
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=150,
                timeout=5.0
            )
            enriched_text = response.choices[0].message.content.strip()
            if enriched_text:
                question.question_text = enriched_text
                question.generated_by = "ai"
        except Exception as e:
            logger.warning(f"LLM Question Enrich failed (fallback to template): {e}")
        return question

    async def create_dynamic_questions(self, candidate_profile: CandidateProfile, target_role: str, domain: str, jd_text: str | None, tier: str) -> list[QuestionItem]:
        cand_skills: list[str] = []
        for g in candidate_profile.skills_taxonomy.model_dump().values():
            if isinstance(g, list):
                for s in g:
                    name = s.get("name", "") if isinstance(s, dict) else str(s)
                    if name:
                        cand_skills.append(name)

        skills_str = ", ".join(cand_skills[:5]) if cand_skills else "chung"
        primary_tech = cand_skills[0] if cand_skills else domain
        database_tech = next((s for s in cand_skills if s.lower() in ["postgresql", "mysql", "redis", "mongodb"]), "Database")

        has_system_design = (tier == "pro" and random.random() < 0.4)
        sys_design_turn = random.choice([1, 3]) if has_system_design else -1
        sys_design_topic = SYSTEM_DESIGN_BANK.get(domain, "Thiết kế một hệ thống chịu tải cao từ đầu.")

        questions: list[QuestionItem] = []
        
        q1 = QuestionItem(
            id=f"q-{uuid.uuid4().hex[:6]}", interviewer=TECH_LEAD_ALEX, category="deep_technical", difficulty="medium",
            context_hint=f"Kiểm tra kinh nghiệm thực tế với {primary_tech}",
            question_text=f"Chào bạn. Tôi là Alex. Tôi thấy bạn có kinh nghiệm với {primary_tech}. Hãy kể về một task khó nhất bạn từng làm với công nghệ này, và cách bạn giải quyết nó?"
        )
        questions.append(q1)

        if sys_design_turn == 1:
            q2 = QuestionItem(id=f"q-{uuid.uuid4().hex[:6]}", interviewer=TECH_LEAD_ALEX, category="system_design_scratch", difficulty="hard", context_hint="Tư duy System Design qua 5 bước", question_text=f"Giờ chúng ta qua bài toán thiết kế. Yêu cầu: {sys_design_topic}. Trước khi vẽ kiến trúc, bạn cần hỏi tôi những constraints (giới hạn) gì để làm rõ đề bài?")
        else:
            q2 = QuestionItem(id=f"q-{uuid.uuid4().hex[:6]}", interviewer=TECH_LEAD_ALEX, category="system_design", difficulty="hard", context_hint=f"Đào sâu xử lý lỗi với {database_tech}", question_text=f"Giả sử cache layer ({database_tech}) bị sập khiến hàng triệu request đánh thẳng vào Primary Database. Bạn sẽ xử lý bài toán Cache Stampede và đảm bảo tính nhất quán dữ liệu như thế nào?")
        questions.append(q2)

        q3 = QuestionItem(
            id=f"q-{uuid.uuid4().hex[:6]}", interviewer=HR_MANAGER_SARAH, category="behavioral_star", difficulty="medium",
            context_hint="Đánh giá kỹ năng giao tiếp, giải quyết bất đồng",
            question_text="Xin phép ngắt lời một chút. Chào bạn, tôi là Sarah (HR). Bạn đã từng gặp trường hợp một kỹ sư senior không đồng ý với giải pháp kỹ thuật của bạn chưa? Bạn đã làm gì để đi đến thống nhất?"
        )
        questions.append(q3)

        if sys_design_turn == 3:
            q4 = QuestionItem(id=f"q-{uuid.uuid4().hex[:6]}", interviewer=TECH_LEAD_ALEX, category="system_design_scratch", difficulty="hard", context_hint="Tư duy System Design", question_text=f"Trở lại với kỹ thuật. Yêu cầu bài toán: {sys_design_topic}. Hãy ước tính tải trọng và mô tả các components chính của High-level design mà bạn chọn?")
        else:
            q4 = QuestionItem(id=f"q-{uuid.uuid4().hex[:6]}", interviewer=HR_MANAGER_SARAH, category="stress_handling", difficulty="medium", context_hint="Quản trị rủi ro deadline", question_text="Khi dự án chỉ còn 3 ngày trước ngày Go-Live mà bạn phát hiện ra một lỗ hổng nghiêm trọng. Nếu release sẽ rủi ro, nhưng nếu hoãn sẽ ảnh hưởng cam kết. Bạn sẽ làm gì?")
        questions.append(q4)

        if tier == "pro":
            q5 = QuestionItem(id=f"q-{uuid.uuid4().hex[:6]}", interviewer=TECH_LEAD_ALEX, category="culture_fit", difficulty="hard", context_hint="Ownership", question_text="Bạn thường làm gì khi phát hiện một đoạn mã legacy rất tệ nhưng không thuộc task của bạn?")
            q6 = QuestionItem(id=f"q-{uuid.uuid4().hex[:6]}", interviewer=HR_MANAGER_SARAH, category="culture_fit", difficulty="medium", context_hint="Định hướng", question_text="Mục tiêu phát triển chuyên môn của bạn trong 2 năm tới là gì? Bạn mong chờ gì ở công ty chúng tôi?")
            questions.extend([q5, q6])

        if tier == "pro":
            jd_str = jd_text or ""
            tasks = [self._enrich_question_with_llm(q, domain, skills_str, jd_str) for q in questions]
            questions = await asyncio.gather(*tasks)

        return questions

    async def start_session(self, candidate_profile: CandidateProfile, target_role: str = "Software Engineer", domain: str = "backend", jd_text: str | None = None, tier: Literal["free", "pro"] = "free") -> InterviewSession:
        session_id = f"session-{uuid.uuid4().hex[:8]}"
        max_turns = 5 if tier == "free" else 6
        questions = await self.create_dynamic_questions(candidate_profile, target_role, domain, jd_text, tier)
        turns = [InterviewTurn(turn_index=idx + 1, question=q, candidate_answer=None, evaluation=None) for idx, q in enumerate(questions[:max_turns])]
        return InterviewSession(
            session_id=session_id, candidate_id=candidate_profile.personal_info.full_name, candidate_name=candidate_profile.personal_info.full_name,
            target_role=target_role, domain=domain, tier=tier, max_turns=max_turns, turns=turns, current_turn_index=0, is_completed=False, final_report=None
        )

    async def _evaluate_with_llm(self, turn: InterviewTurn, answer_text: str, pre_screen_bonus: int, is_sys_design: bool) -> TurnEvaluation:
        client = get_openai_client()
        prompt = f"""
Bạn là AI Judge. Chấm điểm câu trả lời của ứng viên.
Câu hỏi: {turn.question.question_text}
Câu trả lời: {answer_text}
TRẢ VỀ JSON: {{"technical_depth_score":25, "star_structure_score":20, "confidence_score":20, "adaptability_score":15, "feedback":"...", "key_strengths":[".."], "improvement_areas":[".."], "ideal_star_answer":".."}}
"""
        try:
            response = await client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.2, response_format={"type": "json_object"})
            data = json.loads(response.choices[0].message.content.strip())
            tech = min(30, data.get("technical_depth_score", 15) + pre_screen_bonus)
            star = min(25, data.get("star_structure_score", 15))
            conf = min(25, data.get("confidence_score", 15))
            adapt = min(20, data.get("adaptability_score", 15))
            scores = {"tech": tech, "star": star, "conf": conf, "adapt": adapt}
            return TurnEvaluation(
                score=tech + star + conf + adapt, technical_depth_score=tech, star_structure_score=star, confidence_score=conf, adaptability_score=adapt,
                feedback=data.get("feedback", "Tốt."), key_strengths=data.get("key_strengths", []), improvement_areas=data.get("improvement_areas", []),
                ideal_star_answer=data.get("ideal_star_answer", ""), bonus_points=pre_screen_bonus, has_quantified_result=(pre_screen_bonus > 0),
                weak_axis=min(scores, key=scores.get), is_llm_evaluated=True
            )
        except Exception as e:
            logger.warning(f"LLM Eval failed: {e}")
            raise e

    async def _evaluate_with_keyword(self, turn: InterviewTurn, clean_ans: str, word_count: int, pre_screen_bonus: int) -> TurnEvaluation:
        tech_score = 15 + pre_screen_bonus
        if sum(1 for kw in ["cache", "database", "scale", "async", "tối ưu"] if kw in clean_ans.lower()) >= 2: tech_score += 10
        star_score = 20 if "kết quả" in clean_ans.lower() else 15
        conf = 20 if word_count >= 30 else 15
        adapt = 15
        return TurnEvaluation(
            score=min(98, tech_score + star_score + conf + adapt), technical_depth_score=tech_score, star_structure_score=star_score,
            confidence_score=conf, adaptability_score=adapt, feedback="Đánh giá sơ bộ.", key_strengths=[], improvement_areas=[], ideal_star_answer="",
            bonus_points=pre_screen_bonus, has_quantified_result=(pre_screen_bonus > 0), weak_axis="tech", is_llm_evaluated=False
        )

    async def _generate_adversarial_followup(self, turn: InterviewTurn) -> QuestionItem:
        try:
            client = get_openai_client()
            prompt = f"Phản biện lại câu trả lời này cực kỳ ngắn gọn (Alex): {turn.candidate_answer}"
            response = await client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.8, max_tokens=100)
            q_text = response.choices[0].message.content.strip()
        except:
            q_text = "Senior của bạn không đồng ý với giải pháp này. Bạn phản bác ra sao?"
        return QuestionItem(id=f"q-{uuid.uuid4().hex[:6]}", interviewer=TECH_LEAD_ALEX, category="deep_technical", difficulty="hard", question_text=q_text, generated_by="ai", follow_up_of=turn.question.id)

    async def evaluate_turn_answer(self, session: InterviewSession, turn: InterviewTurn, answer_text: str) -> TurnEvaluation:
        clean_ans = answer_text.strip()
        pre_screen_bonus = 3 if any(c.isdigit() or c in "%$" for c in clean_ans) else 0

        if len(clean_ans.split()) < 10:
            eval_result = await self._evaluate_with_keyword(turn, clean_ans, len(clean_ans.split()), 0)
            eval_result.feedback = "Câu trả lời quá ngắn."
        else:
            try:
                eval_result = await self._evaluate_with_llm(turn, clean_ans, pre_screen_bonus, turn.question.category == "system_design_scratch")
            except:
                eval_result = await self._evaluate_with_keyword(turn, clean_ans, len(clean_ans.split()), pre_screen_bonus)

        turn.evaluation = eval_result
        
        if session.tier == "pro" and turn.turn_index == 2 and eval_result.score >= 70 and session.current_turn_index + 1 < len(session.turns):
            session.turns[session.current_turn_index + 1].question = await self._generate_adversarial_followup(turn)

        return eval_result

    def generate_final_assessment(self, session: InterviewSession) -> CandidateAssessmentReport:
        evaluated_turns = [t for t in session.turns if t.evaluation]
        count = len(evaluated_turns)
        if count == 0: return CandidateAssessmentReport(session_id=session.session_id, candidate_name=session.candidate_name, target_role=session.target_role, total_turns_completed=0, overall_score=0, overall_grade="C", verdict="No data", technical_average=0, star_structure_average=0, confidence_average=0, adaptability_average=0, top_strengths=[], critical_growth_areas=[], actionable_prep_tips=[])
        
        avg_score = int(sum(t.evaluation.score for t in evaluated_turns) / count)
        grade = "A+" if avg_score >= 90 else "A" if avg_score >= 80 else "B+" if avg_score >= 70 else "B"
        verdict = "ỨNG VIÊN XUẤT SẮC" if avg_score >= 85 else "PHÙ HỢP TỐT"

        report = CandidateAssessmentReport(
            session_id=session.session_id, candidate_name=session.candidate_name, target_role=session.target_role, total_turns_completed=count,
            overall_score=avg_score, overall_grade=grade, verdict=verdict,
            technical_average=sum(t.evaluation.technical_depth_score for t in evaluated_turns) / count,
            star_structure_average=sum(t.evaluation.star_structure_score for t in evaluated_turns) / count,
            confidence_average=sum(t.evaluation.confidence_score for t in evaluated_turns) / count,
            adaptability_average=sum(t.evaluation.adaptability_score for t in evaluated_turns) / count,
            top_strengths=["Phân tích tốt"] if session.tier == "pro" else ["(Khóa) Nâng cấp Pro để xem"],
            critical_growth_areas=["Cần số liệu cụ thể"] if session.tier == "pro" else ["(Khóa) Nâng cấp Pro để xem"],
            actionable_prep_tips=["Luyện tập STAR"] if session.tier == "pro" else ["Nâng cấp Pro để xem nhận xét và Ideal Answers đầy đủ."],
        )
        if session.tier == "free":
            for t in session.turns:
                if t.evaluation: t.evaluation.ideal_star_answer = "Nâng cấp Pro để xem Benchmark Answer."
        return report
