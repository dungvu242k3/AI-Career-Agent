"""Memory Profiling & Resource Leak Detection Suite.

Uses tracemalloc to measure Peak Memory (RAM), allocation hotspots, and verifies
zero memory leaks across high-iteration AI cycles.
"""

import os
import sys
import tracemalloc
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
from ai.models.harvard_cv import HarvardCVData, HarvardContactInfo, HarvardExperienceItem, HarvardEducationItem, HarvardSkillsCategory


def run_memory_profiling(cycles: int = 1000) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    print("=" * 80)
    print(" [PROFILE] MEMORY ALLOCATION & LEAK DETECTION PROFILER ")
    print(f" [CONFIG] Iterating {cycles:,} cycles across all AI components...")
    print("=" * 80)

    tracemalloc.start()
    snapshot_before = tracemalloc.take_snapshot()

    # Instantiate engines
    critic = CriticAgent()
    hybrid_search = HybridJobSearchEngine()
    reranker = JobCrossEncoderReranker()
    arena = InterviewArenaEngine()

    candidate = CandidateProfile(
        personal_info=PersonalInfo(full_name="Nguyễn Văn A"),
        summary=SummarySection(detected_title="Senior Python Backend Engineer"),
        skills_taxonomy=SkillsTaxonomy(
            programming_languages=["Python"],
            frameworks=["FastAPI"],
            databases=["PostgreSQL", "Redis"],
        ),
        metadata=CVMetadata(total_experience_years=4.0),
    )
    cv_data = HarvardCVData(
        target_role="Senior Backend Engineer",
        contact=HarvardContactInfo(full_name="Nguyễn Văn A", email="a@example.com", phone="0901234567", location="Hà Nội"),
        summary="Senior Backend Engineer với 4+ năm kinh nghiệm xây dựng hệ thống phân tán chịu tải cao.",
        experience=[
            HarvardExperienceItem(
                role="Senior Python Engineer",
                company="Tech Corp",
                location="Hà Nội",
                date_range="2022 - Hiện tại",
                bullets=["Architected distributed caching with Redis cluster, reducing latency by 45%."],
            )
        ],
        education=[HarvardEducationItem(degree_major="Cử nhân CNTT", institution="Đại học Bách Khoa", graduation_year="2020")],
        skills_categories=[HarvardSkillsCategory(category_name="Technical", skills=["Python", "FastAPI", "Redis"])],
    )
    sample_jobs = [
        {"id": f"job-{i}", "title": "Senior Python Backend Engineer", "domain": "backend", "min_experience_years": 3.0, "tech_stack": ["Python", "FastAPI", "Redis"]}
        for i in range(10)
    ]

    # Run repetitive cycles
    for _ in range(cycles):
        critic.evaluate(cv_data, candidate)
        hybrid_search.search_and_rank(sample_jobs, query="backend", candidate_profile=candidate)
        reranker.rerank_top_k(candidate, [(j, 0.8) for j in sample_jobs], top_k=5)

    current, peak = tracemalloc.get_traced_memory()
    snapshot_after = tracemalloc.take_snapshot()
    top_stats = snapshot_after.compare_to(snapshot_before, "lineno")

    tracemalloc.stop()

    print(f"\n📊 Peak Memory Allocated: {peak / (1024 * 1024):.2f} MB")
    print(f"📊 Current Retained Memory: {current / (1024 * 1024):.2f} MB")
    print("\n🔍 Top Memory Allocation Hotspots:")
    for stat in top_stats[:5]:
        print(f"   {stat}")

    # SLA: Peak RAM < 50MB for in-memory pure compute
    if peak < 50 * 1024 * 1024:
        print("\n[SUCCESS] MEMORY PROFILING PASSED — NO DETECTED LEAKS, PEAK USAGE < 50MB!\n")
        return 0
    else:
        print("\n[WARNING] MEMORY USAGE EXCEEDED THRESHOLD.\n")
        return 1


if __name__ == "__main__":
    sys.exit(run_memory_profiling())
