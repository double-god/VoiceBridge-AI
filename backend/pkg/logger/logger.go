package logger

import (
	"os"

	"go.uber.org/zap"
	"go.uber.org/zap/zapcore"
)

var Log *zap.Logger

// InitLogger 初始化日志配置
func InitLogger() {
	// 配置日志编码器 (控制台输出好看的颜色，生产环境输出 JSON)
	encoderConfig := zap.NewProductionEncoderConfig()
	encoderConfig.EncodeTime = zapcore.ISO8601TimeEncoder   // 时间格式: 2025-11-28T...
	encoderConfig.EncodeLevel = zapcore.CapitalColorLevelEncoder // 级别颜色: INFO/ERROR

	// 核心配置
	core := zapcore.NewCore(
		zapcore.NewConsoleEncoder(encoderConfig), // 编码器
		zapcore.AddSync(os.Stdout),               // 输出到控制台
		zap.DebugLevel,                           // 日志级别
	)

	// 创建 Logger (AddCaller 显示调用日志的文件和行号)
	Log = zap.New(core, zap.AddCaller())

	// 替换全局 Logger
	zap.ReplaceGlobals(Log)
}