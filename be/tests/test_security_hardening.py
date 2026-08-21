import asyncio
import uuid

import jwt
from fastapi.testclient import TestClient

from ai.models.interview import InterviewSession
from be.api.v1 import interview_router
from be.api.v1.interview_router import StoredSession, _get_session, _store_session
from be.core.rate_limiter import read_rate_limiter
from be.core.security import CurrentUser, require_current_user
from be.config import get_settings
from be.db.database import save_candidate
from be.main import app


def test_fastapi_resource_endpoint_requires_a_valid_access_token(monkeypatch):
    app.dependency_overrides.pop(require_current_user, None)
    read_rate_limiter.reset()
    monkeypatch.setenv("JWT_SECRET", "a" * 64)
    get_settings.cache_clear()
    token = jwt.encode(
        {
            "sub": "1",
            "email": "user@example.com",
            "tier": "free",
            "iss": "careerpilot-auth",
            "aud": "careerpilot-api",
        },
        "a" * 64,
        algorithm="HS256",
    )

    with TestClient(app) as client:
        assert client.get(f"/api/v1/cv/preview/{uuid.uuid4()}").status_code == 401
        response = client.get(
            f"/api/v1/cv/preview/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404
    get_settings.cache_clear()


def test_candidate_owned_by_another_user_is_not_disclosed():
    candidate_id = str(uuid.uuid4())
    read_rate_limiter.reset()
    with TestClient(app) as client:
        asyncio.run(
            save_candidate(
                profile_json="{}",
                full_name="Private Candidate",
                email="private@example.com",
                title="Engineer",
                owner_user_id=1,
                candidate_id=candidate_id,
            )
        )
        app.dependency_overrides[require_current_user] = lambda: CurrentUser(
            id=2,
            email="other@example.com",
            tier="free",
        )
        assert client.get(f"/api/v1/cv/preview/{candidate_id}").status_code == 404


def test_interview_compare_and_set_rejects_stale_writer(monkeypatch):
    async def no_redis():
        return None

    monkeypatch.setattr(interview_router, "get_redis_client", no_redis)
    interview_router.ACTIVE_SESSIONS.clear()
    session = InterviewSession(
        session_id=str(uuid.uuid4()),
        candidate_id=str(uuid.uuid4()),
        candidate_name="Candidate",
        target_role="Backend Engineer",
    )
    initial = StoredSession(owner_user_id=1, session=session)
    assert asyncio.run(_store_session(initial)) is True

    writer_one = asyncio.run(_get_session(session.session_id))
    writer_two = asyncio.run(_get_session(session.session_id))
    assert writer_one and writer_two
    writer_one.version += 1
    writer_two.version += 1

    assert asyncio.run(_store_session(writer_one, expected_version=0)) is True
    assert asyncio.run(_store_session(writer_two, expected_version=0)) is False
