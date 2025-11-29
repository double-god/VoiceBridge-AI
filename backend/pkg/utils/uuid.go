package utils

import "github.com/google/uuid"

// NewUUID 生成一个新的 UUID v4 字符串
func NewUUID() string {
	return uuid.New().String()
}

// NewShortUUID 生成短格式 UUID（去掉横杠，32 字符）
func NewShortUUID() string {
	u := uuid.New()
	return u.String()[:8] + u.String()[9:13] + u.String()[14:18] + u.String()[19:23] + u.String()[24:]
}
