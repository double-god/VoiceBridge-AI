package logger

import (
	"os"
	"strings"

	"go.uber.org/zap"
	"go.uber.org/zap/zapcore"
)

// Log 全局日志实例
var Log *zap.Logger

// Options 日志配置选项 (解耦：不依赖 config 包，由调用方传入)
type Options struct {
	Level      string // debug, info, warn, error
	Env        string // development, production
	OutputPath string // 日志文件路径 (空则只输出到控制台)
}

// DefaultOptions 默认配置
func DefaultOptions() Options {
	return Options{
		Level: "info",
		Env:   "development",
	}
}

// Init 初始化日志 (接受配置参数，实现解耦)
func Init(opts Options) {
	level := parseLevel(opts.Level)

	// 编码器配置
	encoderConfig := zap.NewProductionEncoderConfig()
	encoderConfig.EncodeTime = zapcore.ISO8601TimeEncoder // 2025-11-28T10:30:00

	var encoder zapcore.Encoder
	if opts.Env == "production" {
		// 生产环境: JSON 格式，便于 ELK 采集
		encoderConfig.EncodeLevel = zapcore.CapitalLevelEncoder
		encoder = zapcore.NewJSONEncoder(encoderConfig)
	} else {
		// 开发环境: 控制台彩色输出
		encoderConfig.EncodeLevel = zapcore.CapitalColorLevelEncoder
		encoder = zapcore.NewConsoleEncoder(encoderConfig)
	}

	// 输出目标
	var writers []zapcore.WriteSyncer
	writers = append(writers, zapcore.AddSync(os.Stdout)) // 始终输出到控制台

	// 可选：同时输出到文件
	if opts.OutputPath != "" {
		file, err := os.OpenFile(opts.OutputPath, os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0644)
		if err == nil {
			writers = append(writers, zapcore.AddSync(file))
		}
	}

	// 组装核心
	core := zapcore.NewCore(
		encoder,
		zapcore.NewMultiWriteSyncer(writers...),
		level,
	)

	// 创建 Logger
	Log = zap.New(core, zap.AddCaller(), zap.AddCallerSkip(0))
	zap.ReplaceGlobals(Log)
}

// InitLogger 兼容旧接口 (无参数版本，使用默认配置)
func InitLogger() {
	Init(DefaultOptions())
}

// parseLevel 解析日志级别字符串
func parseLevel(levelStr string) zapcore.Level {
	switch strings.ToLower(levelStr) {
	case "debug":
		return zap.DebugLevel
	case "info":
		return zap.InfoLevel
	case "warn", "warning":
		return zap.WarnLevel
	case "error":
		return zap.ErrorLevel
	default:
		return zap.InfoLevel
	}
}
