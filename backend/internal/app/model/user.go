package model
import "gorm.io/gorm"

type User struct {
	gorm.Model
	Username string `gorm:"uniqueIndex;type:varchar(100);not null" json:"username"`
	Password string `gorm:"type:varchar(255);not null" json:"-"` // 密码不返回给前端
	Role     string `gorm:"type:varchar(20);default:'patient'" json:"role"`

	//患者画像
	HealthInfo  string `gorm:"type:text" json:"health_info"`  // 健康状况
	Habits      string `gorm:"type:text" json:"habits"`       // 生活习惯
	CommonItems string `gorm:"type:text" json:"common_items"` // 常用物品

	// 关联：一个用户有多条录音
	VoiceRecords []VoiceRecord `gorm:"foreignKey:UserID" json:"voice_records,omitempty"`
}