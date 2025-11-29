package router

import (
	"voicebridge/internal/app/handler"
	"voicebridge/internal/pkg/config"
	"voicebridge/internal/pkg/middleware"

	"github.com/gin-gonic/gin"
)

// Setup 注册所有路由
// Router 不生产 Handler，只是 Handler 的搬运工
func Setup(
	r *gin.Engine,
	cfg *config.Config,
	userH *handler.UserHandler,
	voiceH *handler.VoiceHandler,
) {
	// 全局中间件 (CORS, Logger, Recovery)
	r.Use(gin.Recovery())
	r.Use(middleware.Cors()) // 解决跨域

	// 路由分组
	api := r.Group("/api/v1")
	{
		// 公开接口 (无需 Token)
		authGroup := api.Group("/auth")
		{
			authGroup.POST("/login", userH.Login)
			authGroup.POST("/register", userH.Register)
		}

		// 受保护接口 (需要 JWT Token)
		// 使用 JWT 中间件拦截
		protected := api.Group("/")
		protected.Use(middleware.JWTAuth(cfg))
		{
			// 用户模块
			userGroup := protected.Group("/user")
			{
				userGroup.GET("/profile", userH.GetProfile)
				userGroup.PUT("/profile", userH.UpdateProfile)
			}

			// 语音模块
			voiceGroup := protected.Group("/voice")
			{
				voiceGroup.POST("/upload", voiceH.Upload)
				voiceGroup.GET("/history", voiceH.GetHistory)
				// SSE 接口
				voiceGroup.GET("/status/stream/:id", voiceH.StreamStatus)
			}
		}
	}
}
