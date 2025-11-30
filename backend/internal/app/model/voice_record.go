package model
import "gorm.io/gorm"

type VoiceRecord struct {
	gorm.Model
	UserID      uint   `gorm:"index;not null" json:"user_id"` 	//关联的用户ID

	MinioBucket string `gorm:"type:varchar(100);not null" json:"minio_bucket"` // MinIO存储桶名称
	MinioKey   string `gorm:"type:varchar(255);not null" json:"minio_key"`       // MinIO对象键
	Duration   int    `gorm:"not null" json:"duration"`                     // 录音时长，单位秒

	//状态流转
	//uploaded->分析中->分析完成->失败
	Status string `gorm:"type:varchar(20);default:'uploaded'" json:"status"` // 录音状态

	//关联，一对一关联分析结果
	AnalysisResult AnalysisResult `gorm:"foreignKey:VoiceRecordID" json:"analysis_result,omitempty"`
}