"""Hybrid Dense-Sparse Search Engine combining BM25 keyword matching with Dense Vector Cosine Similarity."""

from typing import Any
from ai.analysis.job_embeddings import JobEmbeddingEngine, compute_cosine_similarity, _tokenize
from ai.models.candidate import CandidateProfile


class HybridJobSearchEngine:
    """Combines BM25-style term frequency matching with dense semantic embeddings."""

    def __init__(self, embedding_engine: JobEmbeddingEngine | None = None):
        self.embedding_engine = embedding_engine or JobEmbeddingEngine()

    def _compute_sparse_score(self, query_tokens: list[str], job_tokens: list[str]) -> float:
        """Compute term overlap score between query and job document."""
        if not query_tokens or not job_tokens:
            return 0.0

        query_set = set(query_tokens)
        job_set = set(job_tokens)

        overlap = query_set.intersection(job_set)
        if not overlap:
            return 0.0

        # Term frequency weighting
        score = len(overlap) / (len(query_set) + 2.0)
        return min(1.0, score)

    def search_and_rank(
        self,
        jobs: list[dict[str, Any]],
        query: str = "",
        candidate_profile: CandidateProfile | None = None,
        domain_filter: str | None = None,
        experience_filter: float | None = None,
    ) -> list[tuple[dict[str, Any], float]]:
        """Run hybrid search over job dataset, ranking results by combined dense-sparse score."""
        if not jobs:
            return []

        # 1. Prepare candidate embedding if profile provided
        cand_vector = None
        cand_tokens = []
        if candidate_profile:
            cand_vector = self.embedding_engine.embed_candidate(candidate_profile)
            cand_skills = []
            for g in candidate_profile.skills_taxonomy.model_dump().values():
                if isinstance(g, list):
                    for s in g:
                        cand_skills.append(s.get("name", "") if isinstance(s, dict) else str(s))
            cand_tokens = _tokenize(f"{candidate_profile.summary.detected_title} {' '.join(cand_skills)}")

        query_tokens = _tokenize(query) if query else []
        combined_tokens = list(set(query_tokens + cand_tokens))

        scored_results: list[tuple[dict[str, Any], float]] = []

        for job in jobs:
            # Apply hard domain filter if given
            if domain_filter and domain_filter.lower() != "all":
                if job.get("domain", "").lower() != domain_filter.lower():
                    continue

            # Apply experience filter if given
            if experience_filter is not None and experience_filter > 0:
                min_exp = float(job.get("min_years_exp", 0) or job.get("min_experience_years", 0))
                # Job requires much more experience than candidate has
                if min_exp > experience_filter + 2.0:
                    continue

            # Document text representation
            raw_stack = job.get("skills", []) or job.get("tech_stack", [])
            tech_stack_str = " ".join([t for t in raw_stack if isinstance(t, str)])
            raw_reqs = job.get("requirements", [])
            reqs_str = raw_reqs if isinstance(raw_reqs, str) else " ".join([r for r in raw_reqs if isinstance(r, str)])

            job_text = (
                f"{job.get('title', '')} "
                f"{job.get('domain', '')} "
                f"{tech_stack_str} "
                f"{reqs_str} "
                f"{job.get('description', '')}"
            )
            job_tokens = _tokenize(job_text)

            # A. Sparse Keyword Score
            sparse_score = self._compute_sparse_score(combined_tokens, job_tokens)

            # B. Dense Vector Score
            job_vector = self.embedding_engine.embed_job(
                title=job.get("title", ""),
                domain=job.get("domain", ""),
                requirements=raw_reqs,
                tech_stack=raw_stack,
                description=job.get("description", ""),
            )

            if cand_vector:
                dense_score = compute_cosine_similarity(cand_vector, job_vector)
            else:
                query_vector = self.embedding_engine.generate_text_vector(query)
                dense_score = compute_cosine_similarity(query_vector, job_vector)

            # C. Hybrid Fusion (50% Sparse + 50% Dense)
            final_hybrid_score = (0.45 * sparse_score) + (0.55 * dense_score)
            scored_results.append((job, final_hybrid_score))

        # Sort descending by hybrid score
        scored_results.sort(key=lambda x: x[1], reverse=True)
        return scored_results
