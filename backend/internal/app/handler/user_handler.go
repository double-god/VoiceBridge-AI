package handler

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

// UserHandler 用户相关接口占位实现（后续可注入 service）
type UserHandler struct{}

func NewUserHandler() *UserHandler { return &UserHandler{} }

func (h *UserHandler) Login(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"action": "login", "status": "stub"})
}

func (h *UserHandler) Register(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"action": "register", "status": "stub"})
}

func (h *UserHandler) GetProfile(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"action": "get_profile", "status": "stub"})
}

func (h *UserHandler) UpdateProfile(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"action": "update_profile", "status": "stub"})
}
