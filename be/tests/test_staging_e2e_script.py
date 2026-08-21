import pytest
import fitz

from scripts import staging_e2e


def test_staging_e2e_refuses_write_without_explicit_opt_in(monkeypatch):
    monkeypatch.delenv("E2E_ALLOW_WRITE", raising=False)
    with pytest.raises(RuntimeError, match="E2E_ALLOW_WRITE=true"):
        staging_e2e.require_write_opt_in()


def test_staging_e2e_builds_a_pdf_and_multipart_payload():
    pdf = staging_e2e.build_minimal_pdf()
    body, boundary = staging_e2e.build_multipart_file("file", "test.pdf", pdf, "application/pdf")

    assert pdf.startswith(b"%PDF-1.4")
    assert b"xref" in pdf
    assert f"--{boundary}".encode() in body
    assert b'filename="test.pdf"' in body
    assert pdf in body

    document = fitz.open(stream=pdf, filetype="pdf")
    assert document.page_count == 1


def test_staging_e2e_accepts_case_insensitive_trace_header():
    response = staging_e2e.HttpResponse(status=404, headers={"X-Trace-Id": "trace-123"}, data={})
    staging_e2e.require_trace("trace check", response)
