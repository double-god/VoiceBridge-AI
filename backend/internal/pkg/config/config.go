package config

import (
	"fmt"
	"os"

	"github.com/joho/godotenv"
)

// config聚合配置项
type Config struct {
	App      AppConfig
	Database DatabaseConfig
	Minio    MinioConfig
	Ai       AIConfig
	JWT      JWTConfig // 新增：集中管理 JWT 相关配置
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

// LoadConfig 加载配置
func LoadConfig() *Config {
	//加载.env文件
	//生产环境可能不用.env文件，而是直接注入环境变量，可以忽略load错误
	_ = godotenv.Load()

	//组装配置
	return &Config{
		App: AppConfig{
			Name: os.Getenv("APP_NAME"),
			Env:  os.Getenv("APP_ENV"),
			Port: os.Getenv("APP_PORT"),
		},
		JWT: JWTConfig{
			Secret: os.Getenv("JWT_SECRET"),
			ExpireMinutes: func() int { // 解析过期时间，默认 60 分钟
				if v := os.Getenv("JWT_EXPIRE_MINUTES"); v != "" {
					var n int
					fmt.Sscanf(v, "%d", &n)
					if n > 0 {
						return n
					}
				}
				return 60
			}(),
		},
		Database: DatabaseConfig{
			Host:     os.Getenv("DB_HOST"),
			Port:     os.Getenv("DB_PORT"),
			User:     os.Getenv("DB_USER"),
			Password: os.Getenv("DB_PASSWORD"),
			DBName:   os.Getenv("DB_NAME"),
		},
		Minio: MinioConfig{
			Endpoint:   os.Getenv("MINIO_ENDPOINT"),
			User:       os.Getenv("MINIO_USER"),
			Password:   os.Getenv("MINIO_PASSWORD"),
			BucketName: os.Getenv("MINIO_BUCKET"),
			UseSSL:     os.Getenv("MINIO_USE_SSL") == "false",
		},
		Ai: AIConfig{
			Host:       os.Getenv("AI_AGENT_HOST"),
			Port:       os.Getenv("AI_AGENT_PORT"),
			ServiceUrl: os.Getenv("AI_AGENT_SERVICE_URL"),
			LLMApiKey:  os.Getenv("AI_AGENT_LLM_API_KEY"),
		},
	}
}
func (c *DatabaseConfig) GetDSN() string {
	// 这里只负责拼字符串，不负责产生数据
	return fmt.Sprintf("host=%s user=%s password=%s dbname=%s port=%s sslmode=disable TimeZone=Asia/Shanghai",
		c.Host, c.User, c.Password, c.DBName, c.Port)
}

// GetAddress 生成 Gin 启动地址
func (c *AppConfig) GetAddress() string {
	return ":" + c.Port
}
