package service

import (
	"fmt"
	"mime/multipart"
	"path/filepath"
	"time"

	"voicebridge/internal/app/model"
	"voicebridge/internal/app/repository"
	"voicebridge/internal/pkg/config"
	"voicebridge/internal/pkg/storage"
	"voicebridge/pkg/utils"
)

type VoiceService struct {
	repo        *repository.VoiceRepo
	agentClient *AgentClient
	minio       *storage.MinioClient
	cfg         *config.Config
}

func NewVoiceService(repo *repository.VoiceRepo, agent *AgentClient, minio *storage.MinioClient, cfg *config.Config) *VoiceService {
	return &VoiceService{
		repo:        repo,
		agentClient: agent,
		minio:       minio,
		cfg:         cfg,
	}
}

// UploadAndProcess 上传录音并触发 AI 分析
func (s *VoiceService) UploadAndProcess(userID uint, file *multipart.FileHeader, duration int) (*model.VoiceRecord, error) {
	// 生成唯一文件名
	// 这样 MinIO 目录结构更清晰
	ext := filepath.Ext(file.Filename)
	dateDir := time.Now().Format("2006/01/02")
	uniqueName := fmt.Sprintf("%s-%s%s", utils.NewUUID(), time.Now().Format("150405"), ext)
	objectName := fmt.Sprintf("voices/%s/%s", dateDir, uniqueName)

	// 上传到 MinIO
	_, _, err := s.minio.UploadFile(file, objectName)
	if err != nil {
		return nil, err
	}

	// 创建数据库记录
	record := &model.VoiceRecord{
		UserID:      userID,
		MinioBucket: s.cfg.Minio.BucketName,
		MinioKey:    objectName,
		Duration:    duration,
		Status:      "uploaded", // 初始状态
	}

	if err := s.repo.Create(record); err != nil {
		return nil, err
	}

	// 异步通知 AI Agent
	// 只要数据库存好了，就可以告诉前端成功了，AI 慢慢算
	s.agentClient.NotifyAgent(record.ID, record.MinioBucket, record.MinioKey)

	return record, nil
}

// GetStatus 获取当前状态用于 SSE
func (s *VoiceService) GetStatus(recordID uint) (*model.VoiceRecord, error) {
	return s.repo.FindByID(recordID)
}

// GetHistory 获取历史列表
func (s *VoiceService) GetHistory(userID uint, page, pageSize int) ([]model.VoiceRecord, int64, error) {
	return s.repo.FindByUserID(userID, page, pageSize)
}

// CancelTask 取消处理任务
func (s *VoiceService) CancelTask(recordID uint, userID uint) error {
	// 查询记录
	record, err := s.repo.FindByID(recordID)
	if err != nil {
		return err
	}

	// 验证所有权
	if record.UserID != userID {
		return fmt.Errorf("无权限取消该任务")
	}

	// 只允许取消处理中的任务
	if record.Status == "completed" || record.Status == "failed" || record.Status == "cancelled" {
		return fmt.Errorf("任务已结束，无法取消")
	}

	// 更新状态为 cancelled
	record.Status = "cancelled"
	return s.repo.Update(record)
}
