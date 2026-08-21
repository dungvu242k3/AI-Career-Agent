"""Stable HTTP mapping for provider-neutral AI failures."""

from fastapi import HTTPException, status

from ai.execution import AIErrorCode, AIExecutionError


def ai_http_error(error: AIExecutionError) -> HTTPException:
    code = error.code
    status_code = {
        AIErrorCode.INPUT_REJECTED: status.HTTP_400_BAD_REQUEST,
        AIErrorCode.BUDGET_EXCEEDED: status.HTTP_429_TOO_MANY_REQUESTS,
        AIErrorCode.TIMEOUT: status.HTTP_504_GATEWAY_TIMEOUT,
        AIErrorCode.PROVIDER_UNAVAILABLE: status.HTTP_503_SERVICE_UNAVAILABLE,
        AIErrorCode.INVALID_RESPONSE: status.HTTP_502_BAD_GATEWAY,
    }[code]
    return HTTPException(status_code=status_code, detail={"code": code.value, "message": str(error)})
