package handler

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

// VoiceHandler 语音相关接口占位实现
type VoiceHandler struct{}

func NewVoiceHandler() *VoiceHandler { return &VoiceHandler{} }

func (h *VoiceHandler) Upload(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"action": "voice_upload", "status": "stub"})
}

func (h *VoiceHandler) GetHistory(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"action": "voice_history", "status": "stub"})
}

func (h *VoiceHandler) StreamStatus(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"action": "voice_stream_status", "status": "stub"})
}
