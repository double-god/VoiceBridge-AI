package main

import (
	"os"
	"os/signal"
	"syscall"

	"voicebridge/internal/pkg/config"
	"voicebridge/internal/pkg/database"
	"voicebridge/pkg/logger"

	"go.uber.org/zap"
)

func main() {
	// 初始化日志
	logger.InitLogger()
	// 程序退出前刷新缓冲
	defer logger.Log.Sync()

	// 加载配置
	cfg := config.LoadConfig()
	logger.Log.Info("服务配置加载完成", zap.String("env", cfg.App.Env))

	// 初始化数据库 (连接 + 迁移)
	// 一行代码搞定，非常解耦。
	// database.Init 内部会自动读取 cfg 里的参数，并自动迁移 internal/model 里的表
	db := database.Init(cfg)
	// (可选) 如果后续 Router 或 Service 需要用到 db，可以传进去
	_ = db


	// 启动服务
	logger.Log.Info("服务已启动，等待请求... (按 Ctrl+C 退出)")

	// 优雅退出机制 (阻塞住主程，直到接收到退出信号)
	quit := make(chan os.Signal, 1)
	// 监听 SIGINT (Ctrl+C) 和 SIGTERM (Docker 停止信号)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	logger.Log.Info("服务正在关闭...")
}