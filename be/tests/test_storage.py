"""Unit tests for Storage Services (LocalStorage & MinIOStorage)."""

from pathlib import Path
import pytest
from be.core.storage import LocalStorageService, MinIOStorageService, get_storage_service


@pytest.mark.asyncio
async def test_local_storage_crud(tmp_path: Path):
    """Test LocalStorageService upload, download, and delete lifecycle."""
    storage = LocalStorageService(base_dir=tmp_path)
    sample_bytes = b"%PDF-1.4 Mock PDF Content"
    filename = "test_cv.pdf"

    # 1. Upload
    storage_key, presigned_url = await storage.upload_file(sample_bytes, filename, user_id="user123")
    assert "user123" in storage_key
    assert storage_key.endswith("test_cv.pdf")
    assert "/api/v1/cv/file/" in presigned_url

    # 2. Download
    retrieved = await storage.get_file_bytes(storage_key)
    assert retrieved == sample_bytes

    # 3. Delete
    deleted = await storage.delete_file(storage_key)
    assert deleted is True

    # 4. Verify Not Found
    with pytest.raises(FileNotFoundError):
        await storage.get_file_bytes(storage_key)


@pytest.mark.asyncio
async def test_minio_storage_fallback_on_unreachable():
    """Test MinIO storage gracefully falls back to local storage when server is offline."""
    storage = MinIOStorageService()
    sample_bytes = b"%PDF-1.4 Fallback test content"

    # Should succeed via local fallback even if MinIO container is not running in test env
    storage_key, presigned_url = await storage.upload_file(sample_bytes, "fallback.pdf")
    assert storage_key.endswith("fallback.pdf")
    assert presigned_url is not None

    retrieved = await storage.get_file_bytes(storage_key)
    assert retrieved == sample_bytes

    await storage.delete_file(storage_key)


def test_get_storage_service_singleton():
    """Test get_storage_service returns a valid instance."""
    service = get_storage_service()
    assert service is not None
