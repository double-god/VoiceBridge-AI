package service

import (
	"context"
	"time"

	"voicebridge/internal/pkg/config"
	"voicebridge/pkg/logger"

	"go.uber.org/zap"
	"gorm.io/gorm"
)

// RetryWorker 定期扫描 uploaded 状态的任务并重试调用 AI Agent
type RetryWorker struct {
	db          *gorm.DB
	agentClient *AgentClient
	cfg         *config.Config
	stopChan    chan struct{}
}

func NewRetryWorker(db *gorm.DB, agentClient *AgentClient, cfg *config.Config) *RetryWorker {
	return &RetryWorker{
		db:          db,
		agentClient: agentClient,
		cfg:         cfg,
		stopChan:    make(chan struct{}),
	}
}

// VoiceRecordRetry 用于查询重试的语音记录
type VoiceRecordRetry struct {
	ID       uint   `gorm:"column:id"`
	UserID   uint   `gorm:"column:user_id"`
	MinioKey string `gorm:"column:minio_key"`
}

// Start 启动重试 worker (阻塞运行，应该在 goroutine 中调用)
func (w *RetryWorker) Start(ctx context.Context) {
	ticker := time.NewTicker(10 * time.Second) // 每 10 秒扫描一次
	defer ticker.Stop()

	logger.Log.Info("重试 Worker 已启动", zap.Duration("interval", 10*time.Second))

	for {
		select {
		case <-ctx.Done():
			logger.Log.Info("重试 Worker 收到停止信号")
			return
		case <-w.stopChan:
			logger.Log.Info("重试 Worker 已停止")
			return
		case <-ticker.C:
			w.retryUploadedTasks()
		}
	}
}

// Stop 停止 worker
func (w *RetryWorker) Stop() {
	close(w.stopChan)
}

// retryUploadedTasks 查找所有 uploaded 状态且创建时间超过 30 秒的任务，重新调用 AI Agent
func (w *RetryWorker) retryUploadedTasks() {
	var records []VoiceRecordRetry

	// 查询 uploaded 状态且创建时间超过 30 秒的记录
	// 使用 30 秒延迟避免与初次上传冲突
	cutoffTime := time.Now().Add(-30 * time.Second)

	err := w.db.Table("voice_records").
		Select("id, user_id, minio_key").
		Where("status = ? AND created_at < ? AND deleted_at IS NULL", "uploaded", cutoffTime).
		Order("created_at ASC"). // 先处理最早的任务
		Limit(10).               // 每次最多处理 10 个，避免阻塞
		Find(&records).Error

	if err != nil {
		logger.Log.Error("查询待重试任务失败", zap.Error(err))
		return
	}

	if len(records) == 0 {
		return // 没有待重试任务
	}

	logger.Log.Info("发现待重试任务",
		zap.Int("count", len(records)),
	)

	// 逐个重试
	for _, record := range records {
		// 将状态临时标记为 processing_asr，避免重复处理
		updateErr := w.db.Table("voice_records").
			Where("id = ? AND status = ?", record.ID, "uploaded").
			Update("status", "processing_asr").Error

		if updateErr != nil {
			logger.Log.Error("更新任务状态失败",
				zap.Uint("record_id", record.ID),
				zap.Error(updateErr),
			)
			continue
		}

		logger.Log.Info("重试调用 AI Agent",
			zap.Uint("record_id", record.ID),
			zap.Uint("user_id", record.UserID),
		)

		// 使用异步通知，不阻塞
		w.agentClient.NotifyAgent(
			record.ID,
			record.UserID,
			w.cfg.Minio.BucketName,
			record.MinioKey,
		)

		// 每个任务之间间隔 2 秒，避免短时间大量请求
		time.Sleep(2 * time.Second)
	}
}
