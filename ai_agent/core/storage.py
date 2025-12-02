from minio import Minio
from .config import settings

# 初始化 MinIO 客户端
client = Minio(
    settings.MINIO_ENDPOINT.replace("http://","").replace("https://",""),
    access_key=settings.MINIO_ROOT_USER,
    secret_key=settings.MINIO_ROOT_PASSWORD,
    secure=settings.MINIO_USE_SSL.lower() == "true"
)

def download_file(bucket: str,object_name: str, file_path: str):
    """从 MinIO 下载文件"""
    client.fget_object(bucket, object_name, file_path)

def upload_file(bucket: str, object_name: str,file_path: str, content_type="audio/wav"):
    """上传文件到 MinIO"""
    client.fput_object(bucket, object_name, file_path, content_type=content_type)