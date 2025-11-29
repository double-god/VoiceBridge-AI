package main

import (
	"net/http"
	"os"
	"os/signal"
	"syscall"

	"github.com/gin-gonic/gin"
	"go.uber.org/zap"

	// 引入内部包
	//	"voicebridge/internal/app/handler"
	//	"voicebridge/internal/app/repository"
	//	"voicebridge/internal/app/service"
	"voicebridge/internal/pkg/config"
	"voicebridge/internal/pkg/database"

	//	"voicebridge/internal/router"
	"voicebridge/pkg/logger"
)

func main() {
	// 1. 基建初始化
	logger.InitLogger()
	defer logger.Log.Sync()

	cfg := config.LoadConfig()
	logger.Log.Info("服务配置加载完成", zap.String("env", cfg.App.Env))

	db := database.Init(cfg)
	// 增量使用 db：健康探测 + 输出连接信息，避免未使用报错
	if sqlDB, err := db.DB(); err == nil {
		if pingErr := sqlDB.Ping(); pingErr != nil {
			logger.Log.Warn("数据库连接可用性检查失败", zap.Error(pingErr))
		} else {
			stats := sqlDB.Stats()
			logger.Log.Info("数据库连接建立成功", zap.Int("open_conns", stats.OpenConnections))
		}
	} else {
		logger.Log.Warn("获取底层数据库连接失败", zap.Error(err))
	}

	//依赖注入

	/*
		// 这里的 NewUserRepo, NewUserService 需要你在对应文件里写好构造函数
		userRepo := repository.NewUserRepo(db)
		userService := service.NewUserService(userRepo, cfg)
		userHandler := handler.NewUserHandler(userService)

		// --- 组装 Voice 模块 ---
		voiceRepo := repository.NewVoiceRepo(db)
		agentClient := service.NewAgentClient(cfg) // Python 客户端
		voiceService := service.NewVoiceService(voiceRepo, agentClient, cfg)
		voiceHandler := handler.NewVoiceHandler(voiceService)
	*/

	// 设置 Gin 模式
	if cfg.App.Env == "production" {
		gin.SetMode(gin.ReleaseMode)
	}

	// 初始化 Gin 引擎
	r := gin.New()

	// 注册路由
	/*router.Setup(r, userHandler, voiceHandler)*/

	// 创建 HTTP Server 实例
	srv := &http.Server{
		Addr:    cfg.App.GetAddress(), // 从 config 获取端口 ":8080"
		Handler: r,
	}

	// 在 Goroutine 中启动服务器 (非阻塞)
	go func() {
		logger.Log.Info("HTTP 服务正在启动...", zap.String("addr", srv.Addr))
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			logger.Log.Fatal("服务器启动失败", zap.Error(err))
		}
	}()

	// 等待中断信号
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit // 阻塞在此，直到收到信号

	logger.Log.Info("正在关闭服务，处理剩余请求...")
	/*
	   // 设置 5 秒超时时间，给正在处理的请求一点时间收尾
	   ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	   defer cancel()

	   	if err := srv.Shutdown(ctx); err != nil {
	   		logger.Log.Fatal("服务强制关闭", zap.Error(err))
	   	}

	   logger.Log.Info("服务已安全停止")
	*/
}
