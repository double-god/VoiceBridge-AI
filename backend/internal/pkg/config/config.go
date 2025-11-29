package config

import (
	"errors"
	"fmt"
	"os"
	"sync"

	"github.com/joho/godotenv"
)

// 单例模式：全局配置只加载一次
var (
	instance *Config
	once     sync.Once
)

// config聚合配置项
type Config struct {
	App      AppConfig
	Database DatabaseConfig
	Minio    MinioConfig
	Ai       AIConfig
	JWT      JWTConfig
	Log      LogConfig // 新增日志配置
}

// 应用基础配置
type AppConfig struct {
	Name string
	Env  string
	Port string
}

// 单独拆分 JWT 配置，避免在 AppConfig 中混杂过多字段
type JWTConfig struct {
	Secret        string // 签名密钥
	ExpireMinutes int    // 过期时间（分钟）
}

// 日志配置
type LogConfig struct {
	Level      string // debug, info, warn, error
	OutputPath string // 日志文件路径
}

// 数据库配置
type DatabaseConfig struct {
	Host     string
	Port     string
	User     string
	Password string
	DBName   string
}

// MinIO配置
type MinioConfig struct {
	Endpoint   string
	User       string
	Password   string
	BucketName string
	UseSSL     bool // 是否使用SSL
}

// AI服务配置
type AIConfig struct {
	Host       string
	Port       string
	ServiceUrl string
	LLMApiKey  string
}

// LoadConfig加载配置，单例模式
func LoadConfig() *Config {
	once.Do(func() {
		// 加载 .env 文件
		_ = godotenv.Load()

		instance = &Config{
			App: AppConfig{
				Name: getEnvWithDefault("APP_NAME", "VoiceBridge"),
				Env:  getEnvWithDefault("APP_ENV", "development"),
				Port: getEnvWithDefault("APP_PORT", "8080"),
			},
			Log: LogConfig{
				Level:      getEnvWithDefault("LOG_LEVEL", "info"),
				OutputPath: os.Getenv("LOG_OUTPUT_PATH"), // 空则只输出到控制台
			},
			JWT: JWTConfig{
				Secret: os.Getenv("JWT_SECRET"),
				ExpireMinutes: func() int {
					var n int
					if v := os.Getenv("JWT_EXPIRE_MINUTES"); v != "" {
						fmt.Sscanf(v, "%d", &n)
						if n > 0 {
							return n
						}
					}
					return 60 // 默认 60 分钟
				}(),
			},
			Database: DatabaseConfig{
				Host:     getEnvWithDefault("DB_HOST", "localhost"),
				Port:     getEnvWithDefault("DB_PORT", "5432"),
				User:     os.Getenv("DB_USER"),
				Password: os.Getenv("DB_PASSWORD"),
				DBName:   os.Getenv("DB_NAME"),
			},
			Minio: MinioConfig{
				Endpoint:   os.Getenv("MINIO_ENDPOINT"),
				User:       os.Getenv("MINIO_USER"),
				Password:   os.Getenv("MINIO_PASSWORD"),
				BucketName: getEnvWithDefault("MINIO_BUCKET", "voicebridge"),
				UseSSL:     os.Getenv("MINIO_USE_SSL") == "true",
			},
			Ai: AIConfig{
				Host:       os.Getenv("AI_AGENT_HOST"),
				Port:       os.Getenv("AI_AGENT_PORT"),
				ServiceUrl: os.Getenv("AI_AGENT_SERVICE_URL"),
				LLMApiKey:  os.Getenv("AI_AGENT_LLM_API_KEY"),
			},
		}
	})
	return instance
}

// Validate 配置校验，启动时调用来检查必填项的
func (c *Config) Validate() error {
	var missing []string

	if c.JWT.Secret == "" {
		missing = append(missing, "JWT_SECRET")
	}
	if c.Database.User == "" {
		missing = append(missing, "DB_USER")
	}
	if c.Database.Password == "" {
		missing = append(missing, "DB_PASSWORD")
	}
	if c.Database.DBName == "" {
		missing = append(missing, "DB_NAME")
	}
	if c.Minio.Endpoint == "" {
		missing = append(missing, "MINIO_ENDPOINT")
	}

	if len(missing) > 0 {
		return errors.New("missing required config: " + fmt.Sprintf("%v", missing))
	}
	return nil
}

// getEnvWithDefault 获取环境变量，为空则返回默认值
func getEnvWithDefault(key, defaultVal string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return defaultVal
}

func (c *DatabaseConfig) GetDSN() string {
	return fmt.Sprintf("host=%s user=%s password=%s dbname=%s port=%s sslmode=disable TimeZone=Asia/Shanghai",
		c.Host, c.User, c.Password, c.DBName, c.Port)
}

// GetAddress 生成 Gin 启动地址
func (c *AppConfig) GetAddress() string {
	return ":" + c.Port
}
