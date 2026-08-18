"""High-Scale Performance Profiling & Latency Benchmark CLI Suite.

Measures P50, P90, P95, P99 latency percentiles, throughput (RPS), and SLA compliance
across all core AI engines (Critic-Actor, Hybrid Search, Job Reranker, Interview Judge).
"""

import os
import sys
import time
from pathlib import Path

# Add project root to sys.path
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from ai.analysis.critic_agent import CriticAgent
from ai.analysis.hybrid_search import HybridJobSearchEngine
from ai.analysis.job_reranker import JobCrossEncoderReranker
from ai.analysis.interview_arena import InterviewArenaEngine
from ai.models.candidate import CandidateProfile, PersonalInfo, SummarySection, SkillsTaxonomy, CVMetadata
from ai.models.harvard_cv import (
    HarvardCVData,
    HarvardContactInfo,
    HarvardExperienceItem,
    HarvardEducationItem,
    HarvardSkillsCategory,
    HarvardProjectItem,
)
from ai.models.interview import InterviewTurn, QuestionItem, InterviewerPersona


def create_sample_candidate() -> CandidateProfile:
    return CandidateProfile(
        personal_info=PersonalInfo(full_name="Nguyễn Văn A"),
        summary=SummarySection(detected_title="Senior Python Backend Engineer"),
        skills_taxonomy=SkillsTaxonomy(
            programming_languages=["Python"],
            frameworks=["FastAPI", "Django"],
            databases=["PostgreSQL", "Redis"],
            devops_and_cloud=["Docker", "Kafka"],
        ),
        metadata=CVMetadata(total_experience_years=4.0),
    )


def create_sample_cv() -> HarvardCVData:
    return HarvardCVData(
        target_role="Senior Backend Engineer",
        contact=HarvardContactInfo(full_name="Nguyễn Văn A", email="a@example.com", phone="0901234567", location="Hà Nội"),
        summary="Senior Backend Engineer với 4+ năm kinh nghiệm xây dựng hệ thống phân tán chịu tải cao.",
        experience=[
            HarvardExperienceItem(
                role="Senior Python Engineer",
                company="Tech Corp",
                location="Hà Nội",
                date_range="2022 - Hiện tại",
                bullets=[
                    "Architected distributed caching with Redis cluster, reducing latency by 45%.",
                    "Spearheaded microservices migration, achieving 99.99% system availability.",
                ],
            )
        ],
        education=[HarvardEducationItem(degree_major="Cử nhân CNTT", institution="Đại học Bách Khoa", graduation_year="2020")],
        skills_categories=[
            HarvardSkillsCategory(category_name="Technical", skills=["Python", "FastAPI", "PostgreSQL", "Redis", "Docker", "Kafka"])
        ],
    )


def calculate_percentiles(durations_ms: list[float]) -> dict[str, float]:
    sorted_d = sorted(durations_ms)
    count = len(sorted_d)
    return {
        "min": sorted_d[0],
        "p50": sorted_d[int(count * 0.50)],
        "p90": sorted_d[int(count * 0.90)],
        "p95": sorted_d[int(count * 0.95)],
        "p99": sorted_d[int(count * 0.99)],
        "max": sorted_d[-1],
        "avg": sum(sorted_d) / count,
    }


def run_benchmarks(iterations: int = 2000) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    print("=" * 80)
    print(" [BENCHMARK] HIGH-SCALE AI ENGINEERING PERFORMANCE & LATENCY PROFILER ")
    print(f" [CONFIG] Iterations per engine: {iterations:,} runs")
    print("=" * 80)

    candidate = create_sample_candidate()
    cv_data = create_sample_cv()

    results = []

    # --- 1. CRITIC AGENT BENCHMARK ---
    critic = CriticAgent()
    durations = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        critic.evaluate(cv_data, candidate)
        durations.append((time.perf_counter() - t0) * 1000.0)

    stats_critic = calculate_percentiles(durations)
    rps_critic = int(1000.0 / stats_critic["avg"])
    sla_critic = stats_critic["p95"] < 5.0
    results.append(("Critic-Actor Reflection (AST & Grounding)", stats_critic, rps_critic, "< 5.0 ms", sla_critic))

    # --- 2. HYBRID VECTOR SEARCH BENCHMARK ---
    hybrid_search = HybridJobSearchEngine()
    sample_jobs = [
        {"id": f"job-{i}", "title": "Senior Python Backend Engineer", "domain": "backend", "min_experience_years": 3.0, "tech_stack": ["Python", "FastAPI", "Redis"]}
        for i in range(20)
    ]
    durations = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        hybrid_search.search_and_rank(sample_jobs, query="backend", candidate_profile=candidate)
        durations.append((time.perf_counter() - t0) * 1000.0)

    stats_hybrid = calculate_percentiles(durations)
    rps_hybrid = int(1000.0 / stats_hybrid["avg"])
    sla_hybrid = stats_hybrid["p95"] < 15.0
    results.append(("Hybrid Dense-Sparse Vector Search", stats_hybrid, rps_hybrid, "< 15.0 ms", sla_hybrid))

    # --- 3. CROSS-ENCODER RERANKER BENCHMARK ---
    reranker = JobCrossEncoderReranker()
    ranked_tuples = [(job, 0.85) for job in sample_jobs[:10]]
    durations = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        reranker.rerank_top_k(candidate, ranked_tuples, top_k=8)
        durations.append((time.perf_counter() - t0) * 1000.0)

    stats_reranker = calculate_percentiles(durations)
    rps_reranker = int(1000.0 / stats_reranker["avg"])
    sla_reranker = stats_reranker["p95"] < 10.0
    results.append(("Cross-Encoder Semantic Re-Ranker", stats_reranker, rps_reranker, "< 10.0 ms", sla_reranker))

    # --- 4. INTERVIEW ARENA JUDGE EVALUATION BENCHMARK ---
    arena = InterviewArenaEngine()
    turn = InterviewTurn(
        turn_index=1,
        question=QuestionItem(
            id="q-1",
            interviewer=InterviewerPersona(name="Alex", role="Tech Lead", avatar_color="#38bdf8", style="Sharp"),
            question_text="How do you handle cache breakdown in Redis?",
            context_hint="Cache stampede defense",
            category="deep_technical",
        ),
    )
    answer_text = "Trong dự án trước khi traffic tăng đột biến, tôi đã thiết kế Redis caching kết hợp rate limiting và Kafka queue."
    durations = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        arena.evaluate_turn_answer(turn, answer_text)
        durations.append((time.perf_counter() - t0) * 1000.0)

    stats_arena = calculate_percentiles(durations)
    rps_arena = int(1000.0 / stats_arena["avg"])
    sla_arena = stats_arena["p95"] < 5.0
    results.append(("Interview Arena Realtime Silent Judge", stats_arena, rps_arena, "< 5.0 ms", sla_arena))

    # --- PRINT RESULTS TABLE ---
    print(f"\n{'ENGINE / SUBSYSTEM':<40} | {'P50 (ms)':<8} | {'P95 (ms)':<8} | {'P99 (ms)':<8} | {'THROUGHPUT':<12} | {'SLA STATUS'}")
    print("-" * 105)
    all_passed = True
    for name, st, rps, target_sla, passed in results:
        status_str = f"[PASS] ({target_sla})" if passed else f"[FAIL] ({target_sla})"
        if not passed:
            all_passed = False
        print(f"{name:<40} | {st['p50']:<8.3f} | {st['p95']:<8.3f} | {st['p99']:<8.3f} | {rps:>6,} req/s | {status_str}")

    print("=" * 105)
    if all_passed:
        print("[SUCCESS] ALL AI SUBSYSTEMS SATISFIED ENTERPRISE HIGH-SCALE SLA TARGETS! \n")
        return 0
    else:
        print("[WARNING] ONE OR MORE SUBSYSTEMS EXCEEDED TARGET LATENCY SLA.\n")
        return 1


if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 2000
    sys.exit(run_benchmarks(count))
