package middleware

//负责gin的拦截逻辑，把utils,config,constant等包引入进来
import (
	"fmt"
	"net/http"
	"strings"
	"time"

	"voicebridge/internal/pkg/config"
	"voicebridge/pkg/constant"
	"voicebridge/pkg/errcode"
	"voicebridge/pkg/logger"
	"voicebridge/pkg/response"
	"voicebridge/pkg/utils"

	"github.com/gin-gonic/gin"
	"go.uber.org/zap"
)

// JWTAuth 接收初始化时加载的配置，避免每次请求重复读取 .env
func JWTAuth(cfg *config.Config) gin.HandlerFunc {
	return func(c *gin.Context) {
		//获取请求头中的token
		tokenHeader := c.GetHeader(constant.TokenHeaderKey)
		if tokenHeader == "" {
			response.Error(c, http.StatusUnauthorized, errcode.ErrTokenMissing)
			c.Abort()
			return
		}
		//校验token格式
		parts := strings.SplitN(tokenHeader, " ", 2)
		if !(len(parts) == 2 && parts[0] == strings.TrimSpace(constant.TokenPrefix)) {
			response.Error(c, http.StatusUnauthorized, errcode.ErrTokenInvalid)
			c.Abort()
			return
		}
		// 解析 token（使用初始化时注入的 cfg，无需每次加载配置）
		claims, err := utils.ParseToken(cfg.JWT.Secret, parts[1])
		if err != nil {
			//统一报过期或未授权，额外记录日志帮助排查
			logger.Log.Warn("token parse failed", zap.Error(err))
			response.Error(c, http.StatusUnauthorized, errcode.TokenInvalid)
			c.Abort()
			return
		}

		// 将用户信息存入上下文
		// 后续 Handler可以通过 c.Get(constant.CtxUserID) 获取
		c.Set(constant.CtxUserID, claims.UserID)
		c.Set(constant.CtxUsername, claims.Username)
		c.Set(constant.CtxRole, claims.Role)

		// 附加：设置一个过期剩余时间头部，帮助前端做刷新策略（演示用，可选）
		if claims.ExpiresAt != nil {
			remaining := time.Until(claims.ExpiresAt.Time).Minutes()
			c.Header("X-Token-Remaining-Minutes", fmt.Sprintf("%.0f", remaining))
		}
		c.Next()
	}
}
