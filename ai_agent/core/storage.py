import os
import tempfile
from pathlib import Path
from minio import Minio
from minio.error import S3Error
from .config import settings

# 初始化 MinIO 客户端
client = Minio(
    settings.MINIO_ENDPOINT.replace("http://", "").replace("https://", ""),
    access_key=settings.MINIO_ROOT_USER,
    secret_key=settings.MINIO_ROOT_PASSWORD,
    secure=settings.MINIO_USE_SSL.lower() == "true",
)

BUCKET_NAME = settings.MINIO_BUCKET


def ensure_bucket():
    """确保 MinIO 存储桶存在"""
    try:
        if not client.bucket_exists(BUCKET_NAME):
            client.make_bucket(BUCKET_NAME)
            print(f"[MinIO] 创建存储桶: {BUCKET_NAME}")
    except S3Error as e:
        print(f"[MinIO] 检查存储桶失败: {e}")


def download_file(object_name: str, local_path: str = None) -> str:
    """从 MinIO 下载文件
    Args:
        object_name: MinIO 对象名称
        local_path: 本地保存路径, 空则使用临时目录
    Returns:
        本地文件路径
    """
    if local_path is None:
        # 临时目录
        temp_dir = tempfile.mkdtemp()
        filename = Path(object_name).name
        local_path = os.path.join(temp_dir, filename)

    # 确保目录存在
    os.makedirs(os.path.dirname(local_path), exist_ok=True)

    try:
        client.fget_object(BUCKET_NAME, object_name, local_path)
        print(f"[MinIO] 下载文件: {object_name} -> {local_path}")
        return local_path
    except S3Error as e:
        print(f"[MinIO] 下载文件失败: {e}")
        raise


def upload_file(local_path: str, object_name: str = None) -> str:
    """上传文件到 MinIO
    Args:
        local_path: 本地文件路径
        object_name: MinIO 对象名称, 空则使用文件名
    Returns:
        MinIO 对象 URL
    """
    ensure_bucket()

    if object_name is None:
        object_name = Path(local_path).name

    try:
        client.fput_object(BUCKET_NAME, object_name, local_path)
        object_url = f"{settings.MINIO_ENDPOINT}/{BUCKET_NAME}/{object_name}"
        print(f"[MinIO] 上传文件: {local_path} -> {object_url}")
        return object_url
    except S3Error as e:
        print(f"[MinIO] 上传文件失败: {e}")
        raise


def delete_file(object_name: str):
    """删除 MinIO 中的文件"""
    try:
        client.remove_object(BUCKET_NAME, object_name)
        print(f"[MinIO] 删除成功: {object_name}")
    except S3Error as e:
        print(f"[MinIO] 删除失败: {e}")
