package database

import (
	// 引入业务模型 (因为要执行迁移，所以依赖业务)
	"voicebridge/internal/app/model"
	// 引入配置 (现在 config 在 internal 里)
	"voicebridge/internal/pkg/config"
	// 引入通用的日志工具 (在 pkg 里)
	"voicebridge/pkg/logger"

	"go.uber.org/zap"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
	gormlogger "gorm.io/gorm/logger"
)

// Init 初始化数据库连接并执行迁移
func Init(cfg *config.Config) *gorm.DB {
	//获取连接字符串 (DSN)
	dsn := cfg.Database.GetDSN()

	// 连接数据库
	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{
		// 设置 GORM 日志级别，打印 SQL
		Logger: gormlogger.Default.LogMode(gormlogger.Info),
	})

	if err != nil {
		// 如果连不上数据库，这是致命错误，直接 Panic 退出
		logger.Log.Fatal("数据库连接失败",
			zap.Error(err),
			// 只记录 Host，不记录密码等敏感信息
			zap.String("host", cfg.Database.Host),
		)
	}
	logger.Log.Info("数据库连接成功")

	// 执行自动迁移
	if err := autoMigrate(db); err != nil {
		logger.Log.Fatal("数据库迁移失败", zap.Error(err))
	}
	logger.Log.Info("数据库表结构同步完成")

	return db
}

// autoMigrate 注册所有需要迁移的模型
func autoMigrate(db *gorm.DB) error {
	return db.AutoMigrate(
		&model.User{},
		&model.VoiceRecord{},
		&model.AnalysisResult{},
	)
}
