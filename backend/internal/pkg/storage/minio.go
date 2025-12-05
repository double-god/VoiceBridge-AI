// 初始化连接，提供简单的上传文件方法
package storage

import (
	"context"
	"fmt"
	"mime/multipart"
	"time"

	"voicebridge/internal/pkg/config"
	"voicebridge/pkg/logger"

	"github.com/minio/minio-go/v7"
	"github.com/minio/minio-go/v7/pkg/credentials"
	"go.uber.org/zap"
)

var (
	minioClient *minio.Client
	bucketName  string
)

type MinioClient struct {
	client     *minio.Client
	bucketName string
}

// InitMinIO 初始化 MinIO 客户端（统一版本）
func InitMinIO(cfg *config.Config) (*MinioClient, error) {
	logger.Log.Info("正在初始化 MinIO 客户端",
		zap.String("endpoint", cfg.Minio.Endpoint),
		zap.String("user", cfg.Minio.User),
		zap.String("bucket", cfg.Minio.BucketName),
		zap.Bool("useSSL", cfg.Minio.UseSSL))

	// 初始化 minio client
	client, err := minio.New(cfg.Minio.Endpoint, &minio.Options{
		Creds:  credentials.NewStaticV4(cfg.Minio.User, cfg.Minio.Password, ""),
		Secure: cfg.Minio.UseSSL,
	})
	if err != nil {
		logger.Log.Error("MinIO 客户端初始化失败", zap.Error(err))
		return nil, err
	}

	logger.Log.Info("MinIO 客户端创建成功，等待 5 秒...")
	time.Sleep(5 * time.Second)

	// 检查 Bucket 是否存在
	ctx := context.Background()
	exists, err := client.BucketExists(ctx, cfg.Minio.BucketName)
	if err != nil {
		logger.Log.Error("检查 Bucket 失败",
			zap.String("bucket", cfg.Minio.BucketName),
			zap.Error(err))
		return nil, err
	}

	// 如果 Bucket 不存在，则创建
	if !exists {
		logger.Log.Info("Bucket 不存在，正在创建...",
			zap.String("bucket", cfg.Minio.BucketName))

		err = client.MakeBucket(ctx, cfg.Minio.BucketName, minio.MakeBucketOptions{})
		if err != nil {
			logger.Log.Error("创建 Bucket 失败",
				zap.String("bucket", cfg.Minio.BucketName),
				zap.Error(err))
			return nil, err
		}

		logger.Log.Info("Bucket 创建成功",
			zap.String("bucket", cfg.Minio.BucketName))
	} else {
		logger.Log.Info("Bucket 已存在",
			zap.String("bucket", cfg.Minio.BucketName))
	}

	// 设置全局变量
	minioClient = client
	bucketName = cfg.Minio.BucketName

	logger.Log.Info("MinIO 存储初始化成功",
		zap.String("endpoint", cfg.Minio.Endpoint),
		zap.String("bucket", cfg.Minio.BucketName),
	)

	return &MinioClient{
		client:     client,
		bucketName: cfg.Minio.BucketName,
	}, nil
}

// UploadFile 上传文件封装了 PutObject
// 返回 minioKey, fileUrl, error
func (m *MinioClient) UploadFile(file *multipart.FileHeader, objectName string) (string, string, error) {
	src, err := file.Open()
	if err != nil {
		return "", "", fmt.Errorf("打开文件失败: %w", err)
	}
	defer src.Close()

	// 上传
	ctx := context.Background()
	info, err := m.client.PutObject(ctx, m.bucketName, objectName, src, file.Size, minio.PutObjectOptions{
		ContentType: file.Header.Get("Content-Type"),
	})
	if err != nil {
		return "", "", fmt.Errorf("上传文件到 MinIO 失败: %w", err)
	}

	logger.Log.Info("文件上传 MinIO 成功",
		zap.String("key", info.Key),
		zap.Int64("size", info.Size))

	// 生成访问 URL
	// 格式: /bucket/key
	fileURL := fmt.Sprintf("/%s/%s", m.bucketName, info.Key)

	return info.Key, fileURL, nil
}

// GetPresignedURL 获取预签名 URL（用于临时访问私有文件）
func (m *MinioClient) GetPresignedURL(objectName string, expiry int) (string, error) {
	ctx := context.Background()

	// 默认 1 小时过期
	if expiry <= 0 {
		expiry = 3600
	}

	presignedURL, err := m.client.PresignedGetObject(ctx, m.bucketName, objectName,
		time.Duration(expiry)*time.Second, nil)
	if err != nil {
		return "", fmt.Errorf("生成预签名 URL 失败: %w", err)
	}

	return presignedURL.String(), nil
}

// DeleteFile 删除文件
func (m *MinioClient) DeleteFile(objectName string) error {
	ctx := context.Background()
	err := m.client.RemoveObject(ctx, m.bucketName, objectName, minio.RemoveObjectOptions{})
	if err != nil {
		return fmt.Errorf("删除文件失败: %w", err)
	}

	logger.Log.Info("文件删除成功", zap.String("key", objectName))
	return nil
}

// GetClient 暴露原生客户端
func (m *MinioClient) GetClient() *minio.Client {
	return m.client
}

// GetGlobalClient 获取全局 MinIO 客户端（兼容旧代码）
func GetGlobalClient() *minio.Client {
	return minioClient
}

// GetBucketName 获取 Bucket 名称
func GetBucketName() string {
	return bucketName
}
