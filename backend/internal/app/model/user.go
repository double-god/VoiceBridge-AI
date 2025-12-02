package model

import "gorm.io/gorm"

type User struct {
	gorm.Model
	Username string `gorm:"uniqueIndex;type:varchar(100);not null" json:"username"`
	Password string `gorm:"type:varchar(255);not null" json:"-"` // 密码不返回给前端
	Role     string `gorm:"type:varchar(20);default:'patient'" json:"role"`

	//患者画像
	Name        string `gorm:"type:varchar(100)" json:"name"` // 显示名称
	Age         int    `gorm:"type:int" json:"age"`           // 年龄
	Condition   string `gorm:"type:text" json:"condition"`    // 健康状况
	Habits      string `gorm:"type:text" json:"habits"`       // 生活习惯
	CommonNeeds string `gorm:"type:text" json:"common_needs"` // 常见需求

	// 关联：一个用户有多条录音
	VoiceRecords []VoiceRecord `gorm:"foreignKey:UserID" json:"voice_records,omitempty"`
}
