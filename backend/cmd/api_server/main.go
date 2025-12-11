package main

import (
	"context"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/gin-gonic/gin"
	"go.uber.org/zap"

	"voicebridge/internal/app/handler"
	"voicebridge/internal/app/repository"
	"voicebridge/internal/app/service"
	"voicebridge/internal/pkg/config"
	"voicebridge/internal/pkg/database"
	"voicebridge/internal/pkg/storage"
	"voicebridge/internal/router"
	"voicebridge/pkg/logger"
)

func main() {
	// 初始化

	// 先加载配置 单例模式，只加载一次
	cfg := config.LoadConfig()

	// 初始化日志
	logger.Init(logger.Options{
		Level:      cfg.Log.Level,
		Env:        cfg.App.Env,
		OutputPath: cfg.Log.OutputPath,
	})
	defer logger.Log.Sync()
	logger.Log.Info("服务配置加载完成", zap.String("env", cfg.App.Env))

	// 校验必填配置
	if err := cfg.Validate(); err != nil {
		logger.Log.Fatal("配置校验失败", zap.Error(err))
	}

	// 初始化数据库
	db := database.Init(cfg)
	if sqlDB, err := db.DB(); err == nil {
		if pingErr := sqlDB.Ping(); pingErr != nil {
			logger.Log.Warn("数据库连接可用性检查失败", zap.Error(pingErr))
		} else {
			stats := sqlDB.Stats()
			logger.Log.Info("数据库连接建立成功", zap.Int("open_conns", stats.OpenConnections))
		}
	}

	// 初始化 MinIO
	minioClient, err := storage.InitMinIO(cfg)
	if err != nil {
		logger.Log.Fatal("MinIO 初始化失败", zap.Error(err))
	}
	logger.Log.Info("MinIO 连接建立成功", zap.String("bucket", cfg.Minio.BucketName))

	// 依赖注入

	// User 模块
	userRepo := repository.NewUserRepo(db)
	userService := service.NewUserService(userRepo, cfg)
	userHandler := handler.NewUserHandler(userService)

	// Voice 模块
	voiceRepo := repository.NewVoiceRepo(db)
	agentClient := service.NewAgentClient(cfg, voiceRepo) // 传入 voiceRepo 失败的时候更新状态
	voiceService := service.NewVoiceService(voiceRepo, agentClient, minioClient, cfg)
	voiceHandler := handler.NewVoiceHandler(voiceService)

	//启动 HTTP 服务

	// 设置 Gin 模式
	if cfg.App.Env == "production" {
		gin.SetMode(gin.ReleaseMode)
	}

	// 初始化 Gin 引擎
	r := gin.New()

	// 注册路由
	router.Setup(r, cfg, userHandler, voiceHandler)

	// 创建 HTTP Server 实例
	srv := &http.Server{
		Addr:    cfg.App.GetAddress(),
		Handler: r,
	}

	// 启动重试 Worker
	retryWorker := service.NewRetryWorker(db, agentClient, cfg)
	workerCtx, workerCancel := context.WithCancel(context.Background())
	defer workerCancel()

	go retryWorker.Start(workerCtx)
	logger.Log.Info("重试 Worker 已启动")

	// 在 Goroutine 中启动服务器 (非阻塞)
	go func() {
		logger.Log.Info("HTTP 服务正在启动...", zap.String("addr", srv.Addr))
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			logger.Log.Fatal("服务器启动失败", zap.Error(err))
		}
	}()

	// 关闭
	// 等待中断信号
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	logger.Log.Info("正在关闭服务，处理剩余请求...")

	// 设置 5 秒超时时间，给正在处理的请求一点时间收尾
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err := srv.Shutdown(ctx); err != nil {
		logger.Log.Fatal("服务强制关闭", zap.Error(err))
	}

	logger.Log.Info("服务已安全停止")
}
