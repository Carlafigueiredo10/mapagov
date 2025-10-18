import os
import logging
from pathlib import Path
from typing import Iterable, Optional

logger = logging.getLogger(__name__)


class BackupUploaderError(Exception):
    pass


class BaseBackupUploader:
    def upload_files(self, files: Iterable[Path], prefix: str = "") -> None:
        raise NotImplementedError


class NoopUploader(BaseBackupUploader):
    def upload_files(self, files: Iterable[Path], prefix: str = "") -> None:
        logger.info("Upload desativado (NoopUploader). Arquivos: %s", [str(f) for f in files])


class S3BackupUploader(BaseBackupUploader):
    def __init__(self, bucket: str, region: Optional[str] = None, base_path: str = "", public: bool = False, endpoint_url: Optional[str] = None):
        import boto3  # import local para não quebrar sem dependência em modos específicos
        # Configurar cliente com endpoint customizado (para Backblaze B2, etc)
        client_kwargs = {}
        if region:
            client_kwargs['region_name'] = region
        if endpoint_url:
            client_kwargs['endpoint_url'] = endpoint_url

        self._s3 = boto3.client("s3", **client_kwargs)
        self.bucket = bucket
        self.base_path = base_path.strip("/")
        self.public = public

    def upload_files(self, files: Iterable[Path], prefix: str = "") -> None:
        uploaded = []
        for f in files:
            if not f.exists():
                logger.warning("Ignorando arquivo inexistente no upload: %s", f)
                continue
            key_parts = [p for p in [self.base_path, prefix.strip('/'), f.name] if p]
            key = "/".join(key_parts)
            extra_args = {"ACL": "public-read"} if self.public else {}
            try:
                self._s3.upload_file(str(f), self.bucket, key, ExtraArgs=extra_args)
                uploaded.append(key)
            except Exception as e:  # noqa
                raise BackupUploaderError(f"Falha ao enviar {f}: {e}") from e
        logger.info("Upload S3 concluído: %s", uploaded)


def build_uploader_from_env() -> BaseBackupUploader:
    """Cria uploader baseado em variáveis de ambiente.

    Variáveis suportadas:
      BACKUP_UPLOAD_PROVIDER=s3|none
      BACKUP_S3_BUCKET=nome-do-bucket
      BACKUP_S3_REGION=us-east-1 (opcional)
      BACKUP_S3_ENDPOINT=https://s3.us-east-005.backblazeb2.com (opcional, para B2/MinIO)
      BACKUP_S3_BASE_PATH=mapagov/backups (opcional)
      BACKUP_S3_PUBLIC=0|1
    """
    provider = os.getenv("BACKUP_UPLOAD_PROVIDER", "none").lower()
    if provider in ("none", "off", "disabled"):
        return NoopUploader()
    if provider == "s3":
        bucket = os.getenv("BACKUP_S3_BUCKET")
        if not bucket:
            raise BackupUploaderError("BACKUP_S3_BUCKET obrigatório para provider s3")
        region = os.getenv("BACKUP_S3_REGION")
        endpoint = os.getenv("BACKUP_S3_ENDPOINT")  # Para Backblaze B2, MinIO, etc
        base = os.getenv("BACKUP_S3_BASE_PATH", "")
        public = os.getenv("BACKUP_S3_PUBLIC", "0") in ("1", "true", "True")
        return S3BackupUploader(bucket=bucket, region=region, base_path=base, public=public, endpoint_url=endpoint)
    raise BackupUploaderError(f"Provider desconhecido: {provider}")
