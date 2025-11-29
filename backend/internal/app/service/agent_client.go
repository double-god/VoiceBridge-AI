package service

import (
	"fmt"
	"time"

	"voicebridge/internal/pkg/config"
	"voicebridge/pkg/logger"

	"github.com/go-resty/resty/v2"
	"go.uber.org/zap"
)

// StatusUpdater 状态更新接口 (解耦：不直接依赖 repository)
type StatusUpdater interface {
	UpdateStatus(id uint, status string) error
}

type AgentClient struct {
	client        *resty.Client
	cfg           *config.Config
	statusUpdater StatusUpdater // 用于失败时更新状态
}

func NewAgentClient(cfg *config.Config, updater StatusUpdater) *AgentClient {
	client := resty.New().
		SetTimeout(30 * time.Second).         // 请求超时 30 秒
		SetRetryCount(3).                     // 最多重试 3 次
		SetRetryWaitTime(1 * time.Second).    // 重试间隔 1 秒
		SetRetryMaxWaitTime(5 * time.Second). // 最大重试间隔 5 秒
		AddRetryCondition(func(r *resty.Response, err error) bool {
			// 网络错误或 5xx 服务端错误时重试
			return err != nil || r.StatusCode() >= 500
		})

	return &AgentClient{
		client:        client,
		cfg:           cfg,
		statusUpdater: updater,
	}
}

// ProcessRequest 发送给 Python 的请求体
type AgentProcessRequest struct {
	RecordID    uint   `json:"record_id"`
	MinioBucket string `json:"minio_bucket"`
	MinioKey    string `json:"minio_key"`
}

// NotifyAgent 异步调用 AI Agent
// 上传成功后立即返回，不阻塞用户请求
func (c *AgentClient) NotifyAgent(recordID uint, bucket, key string) {
	// 启动 goroutine 异步发送
	go func() {
		url := fmt.Sprintf("%s/api/agent/process", c.cfg.Ai.ServiceUrl)
		reqBody := AgentProcessRequest{
			RecordID:    recordID,
			MinioBucket: bucket,
			MinioKey:    key,
		}

		logger.Log.Info("通知 AI Agent 开始处理",
			zap.Uint("record_id", recordID),
			zap.String("url", url),
		)

		resp, err := c.client.R().
			SetHeader("Content-Type", "application/json").
			SetHeader("Authorization", "Bearer "+c.cfg.Ai.LLMApiKey).
			SetBody(reqBody).
			Post(url)

		if err != nil {
			logger.Log.Error("调用 AI Agent 失败 (已重试)",
				zap.Uint("record_id", recordID),
				zap.Error(err),
			)
			// 更新状态为 agent_failed，让前端知道出了问题
			c.markFailed(recordID)
			return
		}

		if resp.IsError() {
			logger.Log.Error("AI Agent 返回错误",
				zap.Uint("record_id", recordID),
				zap.Int("status", resp.StatusCode()),
				zap.String("body", string(resp.Body())),
			)
			// Agent 返回错误也标记失败
			c.markFailed(recordID)
		} else {
			logger.Log.Info("AI Agent 任务接收成功",
				zap.Uint("record_id", recordID),
				zap.Int("status", resp.StatusCode()),
			)
		}
	}()
}

// NotifyAgentSync 同步调用 ，用于需要等待结果的场景
func (c *AgentClient) NotifyAgentSync(recordID uint, bucket, key string) error {
	url := fmt.Sprintf("%s/api/agent/process", c.cfg.Ai.ServiceUrl)
	reqBody := AgentProcessRequest{
		RecordID:    recordID,
		MinioBucket: bucket,
		MinioKey:    key,
	}

	resp, err := c.client.R().
		SetHeader("Content-Type", "application/json").
		SetHeader("Authorization", "Bearer "+c.cfg.Ai.LLMApiKey).
		SetBody(reqBody).
		Post(url)

	if err != nil {
		return fmt.Errorf("调用 AI Agent 失败: %w", err)
	}
	if resp.IsError() {
		return fmt.Errorf("AI Agent 返回错误: status=%d, body=%s", resp.StatusCode(), string(resp.Body()))
	}
	return nil
}

// markFailed 标记任务失败 (内部方法)
func (c *AgentClient) markFailed(recordID uint) {
	if c.statusUpdater == nil {
		return
	}
	if err := c.statusUpdater.UpdateStatus(recordID, "agent_failed"); err != nil {
		logger.Log.Error("更新失败状态到 DB 失败",
			zap.Uint("record_id", recordID),
			zap.Error(err),
		)
	}
}
