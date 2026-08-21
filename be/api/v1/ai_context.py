"""Request-scoped owner binding for AI budgets and metadata-only telemetry."""

from collections.abc import AsyncIterator

from fastapi import Depends

from ai.execution import bind_ai_owner, reset_ai_owner
from be.core.security import CurrentUser, require_current_user


async def ai_request_context(
    current_user: CurrentUser = Depends(require_current_user),
) -> AsyncIterator[None]:
    token = bind_ai_owner(current_user.id)
    try:
        yield
    finally:
        reset_ai_owner(token)
