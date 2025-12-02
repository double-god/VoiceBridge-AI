// 负责解析参数，响应json数据，处理上下文等
package handler

import (
	"net/http"

	"github.com/gin-gonic/gin"

	"voicebridge/internal/app/service"
	"voicebridge/pkg/constant"
	"voicebridge/pkg/errcode"
	"voicebridge/pkg/response"
)

type UserHandler struct {
	svc *service.UserService
}

func NewUserHandler(svc *service.UserService) *UserHandler { return &UserHandler{svc: svc} }

// 请求结构体
type RegisterRequest struct {
	Username string `json:"username" binding:"required"`
	Password string `json:"password" binding:"required"`
}

type LoginRequest struct {
	Username string `json:"username" binding:"required"`
	Password string `json:"password" binding:"required"`
}

type UpdateProfileRequest struct {
	Name        string `json:"name"`
	Age         int    `json:"age"`
	Condition   string `json:"condition"`
	Habits      string `json:"habits"`
	CommonNeeds string `json:"common_needs"`
}

// 注册接口
func (h *UserHandler) Register(c *gin.Context) {
	var req RegisterRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		response.Error(c, http.StatusBadRequest, errcode.InvalidParams)
		return
	}

	// 调用 Service，返回 token
	token, user, err := h.svc.Register(req.Username, req.Password)

	if err != nil {
		if err.Error() == "user exists" {
			response.Error(c, http.StatusConflict, errcode.UserExists)
			return
		}
		// 其他错误
		response.Error(c, http.StatusInternalServerError, errcode.ServerError)
		return
	}

	// 直接返回 Token，前端拿到后直接存 localStorage 并跳转首页
	response.Success(c, gin.H{
		"token": token,
		"user": gin.H{
			"id":         user.ID,
			"username":   user.Username,
			"role":       user.Role,
			"created_at": user.CreatedAt,
		},
	})
}

// Login 登录接口
func (h *UserHandler) Login(c *gin.Context) {
	var req LoginRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		response.Error(c, http.StatusBadRequest, errcode.InvalidParams)
		return
	}

	token, user, err := h.svc.Login(req.Username, req.Password)
	if err != nil {
		// 区分用户不存在还是密码错误
		if err.Error() == "user not found" {
			response.Error(c, http.StatusUnauthorized, errcode.UserNotFound)
			return
		}
		if err.Error() == "password incorrect" {
			response.Error(c, http.StatusUnauthorized, errcode.PasswordIncorrect)
			return
		}
		response.Error(c, http.StatusInternalServerError, errcode.ServerError)
		return
	}

	// 返回数据
	response.Success(c, gin.H{
		"token": token,
		"user": gin.H{
			"id":           user.ID,
			"username":     user.Username,
			"role":         user.Role,
			"name":         user.Name,
			"age":          user.Age,
			"condition":    user.Condition,
			"habits":       user.Habits,
			"common_needs": user.CommonNeeds,
		},
	})
}

// GetProfile 获取画像
func (h *UserHandler) GetProfile(c *gin.Context) {
	// 1. 从 Context 获取当前登录用户 ID (由 JWT 中间件设置)
	uidVal, exists := c.Get(constant.CtxUserID)
	if !exists {
		response.Error(c, http.StatusUnauthorized, errcode.Unauthorized)
		return
	}
	uid := uidVal.(uint) // 类型断言

	// 查询
	user, err := h.svc.GetProfile(uid)
	if err != nil {
		response.Error(c, http.StatusNotFound, errcode.UserNotFound)
		return
	}

	// 返回敏感信息过滤后的数据
	response.Success(c, gin.H{
		"username":     user.Username,
		"name":         user.Name,
		"age":          user.Age,
		"condition":    user.Condition,
		"habits":       user.Habits,
		"common_needs": user.CommonNeeds,
	})
}

// UpdateProfile 更新画像
func (h *UserHandler) UpdateProfile(c *gin.Context) {
	// 1. 获取 ID
	uidVal, exists := c.Get(constant.CtxUserID)
	if !exists {
		response.Error(c, http.StatusUnauthorized, errcode.Unauthorized)
		return
	}
	uid := uidVal.(uint)

	// 2. 解析参数
	var req UpdateProfileRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		response.Error(c, http.StatusBadRequest, errcode.InvalidParams)
		return
	}

	// 构造更新 Map
	updates := gin.H{
		"name":         req.Name,
		"age":          req.Age,
		"condition":    req.Condition,
		"habits":       req.Habits,
		"common_needs": req.CommonNeeds,
	}

	// 4. 执行更新
	if err := h.svc.UpdateProfile(uid, updates); err != nil {
		response.Error(c, http.StatusInternalServerError, errcode.ServerError)
		return
	}

	response.Success(c, nil)
}
