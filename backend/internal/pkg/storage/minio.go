//初始化连接，提供简单的上传文件方法
package storage
import(
	"context"
	"fmt"
	"mime/multipart"

	"voicebridge/internal/pkg/config"
	"voicebridge/pkg/logger"

	"github.com/minio/minio-go/v7"
	"github.com/minio/minio-go/v7/pkg/credentials"
	"go.uber.org/zap"
)

type MinioClient struct {
	client *minio.Client
	bucketName string
}

//Init初始化minIO客户端
func Init(cfg *config.Config) *MinioClient {
	//初始化minio client
	client, err :=minio.New(cfg.Minio.Endpoint,&minio.Options{
		Creds:  credentials.NewStaticV4(cfg.Minio.User, cfg.Minio.Password, ""),
		Secure: cfg.Minio.UseSSL,
	})
	if err != nil {
		logger.Log.Fatal("MinIO 连接失败", zap.Error(err))
	}

	// 检查 Bucket 是否存在，不存在则创建 (自动初始化)
	ctx := context.Background()
	exists, err := client.BucketExists(ctx, cfg.Minio.BucketName)
	if err != nil {
		logger.Log.Fatal("检查 Bucket 失败", zap.String("bucket", cfg.Minio.BucketName), zap.Error(err))
	}
	if !exists {
		err = client.MakeBucket(ctx, cfg.Minio.BucketName, minio.MakeBucketOptions{})
		if err != nil {
			logger.Log.Fatal("创建 Bucket 失败", zap.Error(err))
		}
		logger.Log.Info(" MinIO Bucket 创建成功", zap.String("bucket", cfg.Minio.BucketName))
	}

	return &MinioClient{
		client:     client,
		bucketName: cfg.Minio.BucketName,
	}
}

// UploadFile 上传文件 (封装了 PutObject)
// 返回minioKey, fileUrl, error
func (m *MinioClient) UploadFile(file *multipart.FileHeader, objectName string) (string, string, error) {
	src, err := file.Open()
	if err != nil {
		return "", "", err
	}
	defer src.Close()

	// 上传
	info, err := m.client.PutObject(context.Background(), m.bucketName, objectName, src, file.Size, minio.PutObjectOptions{
		ContentType: file.Header.Get("Content-Type"),
	})
	if err != nil {
		return "", "", err
	}

	logger.Log.Info("文件上传 MinIO 成功", zap.String("key", info.Key))

	// 生成预览/访问 URL (这里简单拼接，生产环境可能需要 PresignedURL 或 CDN)
	// 格式: http://endpoint/bucket/key
	// 注意：如果 Endpoint 是 localhost，前端可能访问不到容器内的 localhost，这里先返回 key 供后端逻辑使用
	// 前端展示 URL 可以由后端拼装
	return info.Key, fmt.Sprintf("/%s/%s", m.bucketName, info.Key), nil
}

// GetClient 暴露原生客户端 (备用)
func (m *MinioClient) GetClient() *minio.Client {
	return m.client
}