import pytest

from be.core.security import CurrentUser, require_current_user
from be.main import app


@pytest.fixture(autouse=True)
def authenticated_api_client():
    """Keep legacy API behavior tests focused on their endpoint concern.

    Authentication/authorization is covered separately; test requests in this
    suite represent a stable signed-in user that owns fixture data.
    """
    app.dependency_overrides[require_current_user] = lambda: CurrentUser(
        id=1,
        email="test@example.com",
        tier="free",
    )
    yield
    app.dependency_overrides.clear()
