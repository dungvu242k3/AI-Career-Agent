"""Safe, opt-in end-to-end checks for a disposable staging environment.

Required environment variables:
  E2E_ALLOW_WRITE=true
  E2E_AUTH_API_URL=https://auth.staging.example/api/v1/auth
  E2E_BACKEND_API_URL=https://api.staging.example/api/v1

Optional:
  E2E_RUN_ASYNC_JOB=true  Enqueues a CV-ingestion job and checks owner isolation.

The script creates two throwaway users. Run it only against a staging database
with a test-data retention policy; it deliberately refuses to run without the
explicit write opt-in. The async-job portion may invoke a worker and an AI
provider, so it is separately opt-in as well.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
import sys
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen
import uuid


DEFAULT_TIMEOUT_SECONDS = 10
_UNKNOWN_JOB_ID = "00000000-0000-0000-0000-000000000000"


@dataclass(frozen=True)
class HttpResponse:
    status: int
    headers: dict[str, str]
    data: Any


def env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise RuntimeError(f"{name} must be true or false")


def require_write_opt_in() -> None:
    if not env_flag("E2E_ALLOW_WRITE"):
        raise RuntimeError("Set E2E_ALLOW_WRITE=true to run staging checks that create test users")


def required_url(name: str) -> str:
    value = os.getenv(name, "").strip().rstrip("/")
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise RuntimeError(f"{name} must be an absolute http(s) URL")
    return value


def _decode_payload(raw: bytes) -> Any:
    if not raw:
        return None
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {"non_json_response": True}


def request(
    method: str,
    url: str,
    *,
    body: bytes | None = None,
    headers: dict[str, str] | None = None,
) -> HttpResponse:
    request_headers = {"Accept": "application/json"}
    if headers:
        request_headers.update(headers)
    http_request = Request(url, data=body, method=method, headers=request_headers)
    try:
        with urlopen(http_request, timeout=DEFAULT_TIMEOUT_SECONDS) as response:
            return HttpResponse(
                status=response.status,
                headers=dict(response.headers.items()),
                data=_decode_payload(response.read()),
            )
    except HTTPError as error:
        return HttpResponse(
            status=error.code,
            headers=dict(error.headers.items()),
            data=_decode_payload(error.read()),
        )
    except URLError as error:
        raise RuntimeError(f"Could not reach {urlparse(url).netloc}: {error.reason}") from error


def expect_status(label: str, response: HttpResponse, expected: int) -> None:
    if response.status != expected:
        raise RuntimeError(f"{label}: expected HTTP {expected}, received HTTP {response.status}")


def require_trace(label: str, response: HttpResponse) -> None:
    has_trace = any(name.lower() == "x-trace-id" and value for name, value in response.headers.items())
    if not has_trace:
        raise RuntimeError(f"{label}: backend response is missing X-Trace-ID")


def json_request(method: str, url: str, payload: dict[str, Any], headers: dict[str, str] | None = None) -> HttpResponse:
    return request(
        method,
        url,
        body=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", **(headers or {})},
    )


def create_and_login_user(auth_api_url: str) -> str:
    token = uuid.uuid4().hex
    email = f"staging-e2e-{token}@example.invalid"
    password = f"Aa1!{token[:24]}"
    register = json_request(
        "POST",
        f"{auth_api_url}/register",
        {"email": email, "password": password},
    )
    expect_status("register staging user", register, 201)

    login = json_request(
        "POST",
        f"{auth_api_url}/login",
        {"email": email, "password": password},
    )
    expect_status("login staging user", login, 200)
    access_token = login.data.get("accessToken") if isinstance(login.data, dict) else None
    if not isinstance(access_token, str) or not access_token:
        raise RuntimeError("login staging user: accessToken is missing")
    return access_token


def bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def build_minimal_pdf() -> bytes:
    """Return a valid, single-page PDF without requiring a PDF library."""
    stream = b"BT\n/F1 12 Tf\n72 720 Td\n(CareerPilot staging E2E) Tj\nET\n"
    objects = (
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"endstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    )
    payload = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, value in enumerate(objects, start=1):
        offsets.append(len(payload))
        payload.extend(f"{index} 0 obj\n".encode("ascii"))
        payload.extend(value)
        payload.extend(b"\nendobj\n")
    xref_offset = len(payload)
    payload.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    payload.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        payload.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    payload.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("ascii")
    )
    return bytes(payload)


def build_multipart_file(field_name: str, filename: str, content: bytes, content_type: str) -> tuple[bytes, str]:
    boundary = f"----CareerPilotE2E{uuid.uuid4().hex}"
    body = bytearray()
    body.extend(f"--{boundary}\r\n".encode("ascii"))
    body.extend(f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"\r\n'.encode("utf-8"))
    body.extend(f"Content-Type: {content_type}\r\n\r\n".encode("ascii"))
    body.extend(content)
    body.extend(f"\r\n--{boundary}--\r\n".encode("ascii"))
    return bytes(body), boundary


def verify_token_contract(backend_api_url: str, access_token: str) -> None:
    owned = request("GET", f"{backend_api_url}/ai-jobs/{_UNKNOWN_JOB_ID}", headers=bearer(access_token))
    expect_status("backend accepts Auth-issued token", owned, 404)
    require_trace("backend token contract", owned)

    invalid = request(
        "GET",
        f"{backend_api_url}/ai-jobs/{_UNKNOWN_JOB_ID}",
        headers=bearer("not-a-valid-jwt"),
    )
    expect_status("backend rejects malformed token", invalid, 401)
    require_trace("backend malformed-token response", invalid)


def verify_async_job_owner_isolation(backend_api_url: str, owner_token: str, other_token: str) -> None:
    idempotency_key = uuid.uuid4().hex
    body, boundary = build_multipart_file(
        "file",
        "staging-e2e.pdf",
        build_minimal_pdf(),
        "application/pdf",
    )
    headers = {
        **bearer(owner_token),
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Idempotency-Key": idempotency_key,
    }
    created = request("POST", f"{backend_api_url}/ai-jobs/cv-ingestion", body=body, headers=headers)
    expect_status("enqueue staging AI job", created, 202)
    require_trace("enqueue staging AI job", created)
    job_id = created.data.get("job_id") if isinstance(created.data, dict) else None
    if not isinstance(job_id, str) or not job_id:
        raise RuntimeError("enqueue staging AI job: job_id is missing")

    duplicate = request("POST", f"{backend_api_url}/ai-jobs/cv-ingestion", body=body, headers=headers)
    expect_status("idempotent enqueue", duplicate, 202)
    duplicate_job_id = duplicate.data.get("job_id") if isinstance(duplicate.data, dict) else None
    if duplicate_job_id != job_id:
        raise RuntimeError("idempotent enqueue returned a different job_id")

    owner_read = request("GET", f"{backend_api_url}/ai-jobs/{job_id}", headers=bearer(owner_token))
    expect_status("owner can read own job", owner_read, 200)
    require_trace("owner reads own job", owner_read)

    other_read = request("GET", f"{backend_api_url}/ai-jobs/{job_id}", headers=bearer(other_token))
    expect_status("other user cannot read owner job", other_read, 404)
    require_trace("other user job isolation", other_read)


def main() -> int:
    try:
        require_write_opt_in()
        auth_api_url = required_url("E2E_AUTH_API_URL")
        backend_api_url = required_url("E2E_BACKEND_API_URL")

        owner_token = create_and_login_user(auth_api_url)
        verify_token_contract(backend_api_url, owner_token)
        print("PASS auth-to-backend token contract")

        if env_flag("E2E_RUN_ASYNC_JOB"):
            other_token = create_and_login_user(auth_api_url)
            verify_async_job_owner_isolation(backend_api_url, owner_token, other_token)
            print("PASS async-job idempotency and owner isolation")
        else:
            print("SKIP async-job owner isolation (set E2E_RUN_ASYNC_JOB=true in dedicated staging)")
    except RuntimeError as error:
        print(f"FAIL {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
