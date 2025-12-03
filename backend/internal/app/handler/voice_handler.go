package handler

import (
	"io"
	"net/http"
	"strconv"
	"time"

	"voicebridge/internal/app/service"
	"voicebridge/pkg/constant"
	"voicebridge/pkg/errcode"
	"voicebridge/pkg/logger"
	"voicebridge/pkg/response"

	"github.com/gin-gonic/gin"
	"go.uber.org/zap"
)

type VoiceHandler struct {
	svc *service.VoiceService
}

func NewVoiceHandler(svc *service.VoiceService) *VoiceHandler {
	return &VoiceHandler{svc: svc}
}

// Upload 上传接口
func (h *VoiceHandler) Upload(c *gin.Context) {
	// 获取 UserID
	uidVal, exists := c.Get(constant.CtxUserID)
	if !exists {
		response.Error(c, http.StatusUnauthorized, errcode.Unauthorized)
		return
	}
	uid := uidVal.(uint)

	// 获取文件
	file, err := c.FormFile("file")
	if err != nil {
		response.Error(c, http.StatusBadRequest, errcode.InvalidParams)
		return
	}

	// 校验大小
	// 5MB = 5 * 1024 * 1024
	if file.Size > 5*1024*1024 {
		response.Error(c, http.StatusRequestEntityTooLarge, errcode.FileTooLarge)
		return
	}

	// 获取时长
	durationStr := c.PostForm("duration")
	duration, _ := strconv.Atoi(durationStr)

	// 调用 Service
	record, err := h.svc.UploadAndProcess(uid, file, duration)
	if err != nil {
		logger.Log.Error("上传处理失败", zap.Error(err))
		response.Error(c, http.StatusInternalServerError, errcode.UploadFailed)
		return
	}

	// 成功返回
	response.Success(c, map[string]interface{}{
		"record_id":    record.ID,
		"status":       record.Status,
		"minio_bucket": record.MinioBucket,
		"minio_key":    record.MinioKey,
		"duration":     record.Duration,
	})
}

// StreamStatus SSE 实时流接口
func (h *VoiceHandler) StreamStatus(c *gin.Context) {
	idStr := c.Param("id")
	recordID, err := strconv.Atoi(idStr)
	if err != nil {
		response.Error(c, http.StatusBadRequest, errcode.InvalidParams)
		return
	}

	//  设置 SSE 头
	c.Writer.Header().Set("Content-Type", "text/event-stream")
	c.Writer.Header().Set("Cache-Control", "no-cache")
	c.Writer.Header().Set("Connection", "keep-alive")
	c.Writer.Header().Set("Access-Control-Allow-Origin", "*")

	clientGone := c.Request.Context().Done()

	// 开始推流循环
	c.Stream(func(w io.Writer) bool {
		select {
		case <-clientGone:
			return false // 客户端断开
		default:
			// 查询最新状态
			record, err := h.svc.GetStatus(uint(recordID))
			if err != nil {
				// If record not found, push error event then close
				c.SSEvent("message", map[string]interface{}{
					"status": "error", "msg": "Record not found",
				})
				return false
			}

			// 构造数据
			data := map[string]interface{}{
				"status":   record.Status,
				"progress": calculateProgress(record.Status),
			}

			// If completed, include result
			if record.Status == "completed" && record.AnalysisResult.ID != 0 {
				data["asr_text"] = record.AnalysisResult.AsrText
				data["refined_text"] = record.AnalysisResult.RefinedText
				data["tts_url"] = record.AnalysisResult.TtsAudioUrl
				data["decision"] = record.AnalysisResult.Decision
			}

			// 推送事件
			c.SSEvent("message", data)

			// 终止条件
			if record.Status == "completed" || record.Status == "failed" {
				return false
			}

			// 轮询间隔
			time.Sleep(500 * time.Millisecond)
			return true
		}
	})
}

// GetHistory 历史记录接口
func (h *VoiceHandler) GetHistory(c *gin.Context) {
	uidVal, _ := c.Get(constant.CtxUserID)
	uid := uidVal.(uint)

	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	pageSize, _ := strconv.Atoi(c.DefaultQuery("page_size", "10"))

	records, total, err := h.svc.GetHistory(uid, page, pageSize)
	if err != nil {
		response.Error(c, http.StatusInternalServerError, errcode.ServerError)
		return
	}

	response.Success(c, map[string]interface{}{
		"list":  records,
		"total": total,
	})
}

// 算进度条
func calculateProgress(status string) int {
	switch status {
	case "uploaded":
		return 10
	case "processing_asr":
		return 30
	case "processing_llm":
		return 60
	case "processing_tts":
		return 80
	case "completed":
		return 100
	default:
		return 0
	}
}
