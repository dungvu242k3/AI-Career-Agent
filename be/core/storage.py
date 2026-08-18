"""Object Storage Service — S3 / MinIO and Local File Storage.

Provides secure file storage, bucket management, and time-limited Presigned URLs
for user document access (PDF & DOCX).
"""

from abc import ABC, abstractmethod
from datetime import timedelta
import io
import logging
from pathlib import Path
import uuid
from minio import Minio
from minio.error import S3Error

from be.config import get_settings

logger = logging.getLogger(__name__)


class BaseStorageService(ABC):
    """Abstract storage interface for file uploads and presigned URL access."""

    @abstractmethod
    async def upload_file(
        self,
        content: bytes,
        filename: str,
        content_type: str = "application/octet-stream",
        user_id: str | None = None,
    ) -> tuple[str, str]:
        """Upload file and return (storage_key, presigned_view_url)."""
        pass

    @abstractmethod
    async def get_file_bytes(self, storage_key: str) -> bytes:
        """Download raw file bytes from storage."""
        pass

    @abstractmethod
    async def delete_file(self, storage_key: str) -> bool:
        """Delete file from storage."""
        pass

    @abstractmethod
    async def get_presigned_url(self, storage_key: str, expiry_seconds: int = 900) -> str:
        """Generate time-limited Presigned GET URL for secure viewing."""
        pass


class LocalStorageService(BaseStorageService):
    """Local filesystem storage service (Offline dev / fallback)."""

    def __init__(self, base_dir: Path | None = None):
        self.base_dir = base_dir or get_settings().upload_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def upload_file(
        self,
        content: bytes,
        filename: str,
        content_type: str = "application/octet-stream",
        user_id: str | None = None,
    ) -> tuple[str, str]:
        file_id = uuid.uuid4().hex[:8]
        safe_name = Path(filename).name
        subfolder = f"users/{user_id}" if user_id else "general"
        target_dir = self.base_dir / subfolder
        target_dir.mkdir(parents=True, exist_ok=True)

        storage_key = f"{subfolder}/{file_id}_{safe_name}"
        file_path = self.base_dir / storage_key
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(content)

        presigned_url = await self.get_presigned_url(storage_key)
        return storage_key, presigned_url

    async def get_file_bytes(self, storage_key: str) -> bytes:
        # Enforce canonical path boundary to prevent Path Traversal
        safe_key = Path(storage_key).as_posix().lstrip("/")
        resolved_path = (self.base_dir / safe_key).resolve()
        resolved_base = self.base_dir.resolve()

        if not str(resolved_path).startswith(str(resolved_base)):
            logger.warning("Path traversal attempt blocked: %s", storage_key)
            raise PermissionError("Truy cập tệp ngoài thư mục cho phép bị từ chối.")

        if not resolved_path.exists() or not resolved_path.is_file():
            raise FileNotFoundError(f"File not found: {storage_key}")

        return resolved_path.read_bytes()

    async def delete_file(self, storage_key: str) -> bool:
        safe_key = Path(storage_key).as_posix().lstrip("/")
        resolved_path = (self.base_dir / safe_key).resolve()
        resolved_base = self.base_dir.resolve()

        if not str(resolved_path).startswith(str(resolved_base)):
            logger.warning("Path traversal delete attempt blocked: %s", storage_key)
            return False

        if resolved_path.exists() and resolved_path.is_file():
            resolved_path.unlink()
            return True
        return False

    async def get_presigned_url(self, storage_key: str, expiry_seconds: int = 900) -> str:
        settings = get_settings()
        safe_key = Path(storage_key).as_posix().lstrip("/")
        return f"{settings.api_prefix}/cv/file/{safe_key}"


class MinIOStorageService(BaseStorageService):
    """High-performance S3-compatible MinIO Object Storage Service."""

    def __init__(self):
        self.settings = get_settings()
        self.bucket_name = self.settings.minio_bucket
        self._client: Minio | None = None
        self._local_fallback = LocalStorageService(self.settings.upload_dir)
        self._init_minio_client()

    def _init_minio_client(self):
        """Initialize MinIO client and ensure bucket exists."""
        try:
            import urllib3
            http_client = urllib3.PoolManager(
                timeout=urllib3.Timeout(connect=0.8, read=1.5),
                retries=False,
            )
            self._client = Minio(
                endpoint=self.settings.minio_endpoint,
                access_key=self.settings.minio_access_key.get_secret_value(),
                secret_key=self.settings.minio_secret_key.get_secret_value(),
                secure=self.settings.minio_secure,
                http_client=http_client,
            )
            # Create bucket if not exists
            if not self._client.bucket_exists(self.bucket_name):
                self._client.make_bucket(self.bucket_name)
                logger.info("Created MinIO bucket: %s", self.bucket_name)
        except Exception as e:
            logger.warning(
                "Could not connect to MinIO at %s (%s). Operating in Local Storage fallback mode.",
                self.settings.minio_endpoint,
                e,
            )
            self._client = None

    async def upload_file(
        self,
        content: bytes,
        filename: str,
        content_type: str = "application/octet-stream",
        user_id: str | None = None,
    ) -> tuple[str, str]:
        if not self._client:
            return await self._local_fallback.upload_file(content, filename, content_type, user_id)

        file_id = uuid.uuid4().hex[:8]
        safe_name = Path(filename).name
        subfolder = f"users/{user_id}" if user_id else "general"
        storage_key = f"{subfolder}/{file_id}_{safe_name}"

        try:
            data_stream = io.BytesIO(content)
            self._client.put_object(
                bucket_name=self.bucket_name,
                object_name=storage_key,
                data=data_stream,
                length=len(content),
                content_type=content_type,
            )
            presigned_url = await self.get_presigned_url(storage_key)
            return storage_key, presigned_url
        except Exception as e:
            logger.warning("MinIO upload failed (%s). Falling back to local storage.", e)
            return await self._local_fallback.upload_file(content, filename, content_type, user_id)

    async def get_file_bytes(self, storage_key: str) -> bytes:
        if not self._client:
            return await self._local_fallback.get_file_bytes(storage_key)

        try:
            response = self._client.get_object(self.bucket_name, storage_key)
            try:
                return response.read()
            finally:
                response.close()
                response.release_conn()
        except Exception as e:
            logger.warning("MinIO download failed (%s). Checking local storage.", e)
            return await self._local_fallback.get_file_bytes(storage_key)

    async def delete_file(self, storage_key: str) -> bool:
        if not self._client:
            return await self._local_fallback.delete_file(storage_key)

        try:
            self._client.remove_object(self.bucket_name, storage_key)
            return True
        except Exception:
            return await self._local_fallback.delete_file(storage_key)

    async def get_presigned_url(self, storage_key: str, expiry_seconds: int = 900) -> str:
        if not self._client:
            return await self._local_fallback.get_presigned_url(storage_key, expiry_seconds)

        try:
            url = self._client.get_presigned_url(
                "GET",
                bucket_name=self.bucket_name,
                object_name=storage_key,
                expires=timedelta(seconds=expiry_seconds),
            )
            return url
        except Exception as e:
            logger.warning("MinIO presigned URL generation failed: %s", e)
            return await self._local_fallback.get_presigned_url(storage_key, expiry_seconds)


_storage_service: BaseStorageService | None = None


def get_storage_service() -> BaseStorageService:
    """Singleton factory for storage service based on configuration."""
    global _storage_service
    if _storage_service is None:
        settings = get_settings()
        if settings.storage_backend == "minio":
            _storage_service = MinIOStorageService()
        else:
            _storage_service = LocalStorageService(settings.upload_dir)
    return _storage_service
