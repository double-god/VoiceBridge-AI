package model

import "gorm.io/gorm"

type VoiceRecord struct {
	gorm.Model
	UserID uint `gorm:"index;not null" json:"user_id"` //关联的用户ID

	MinioBucket string `gorm:"type:varchar(100);not null" json:"minio_bucket"` // MinIO存储桶名称
	MinioKey    string `gorm:"type:varchar(255);not null" json:"minio_key"`    // MinIO对象键
	Duration    int    `gorm:"not null" json:"duration"`                       // 录音时长,单位秒

	// AI Agent 需要的字段
	AudioURL    string `gorm:"type:varchar(500)" json:"audio_url"` // 音频文件 URL
	RawText     string `gorm:"type:text" json:"raw_text"`          // ASR 原始识别文本
	RefinedText string `gorm:"type:text" json:"refined_text"`      // LLM 精炼后的文本
	Confidence  string `gorm:"type:varchar(10)" json:"confidence"` // 置信度
	Decision    string `gorm:"type:varchar(20)" json:"decision"`   // 决策结果 accept/reject
	Reason      string `gorm:"type:text" json:"reason"`            // 决策原因
	TtsURL      string `gorm:"type:varchar(500)" json:"tts_url"`   // TTS 音频 URL

	//状态流转
	//uploaded->processing_asr->processing_llm->processing_tts->completed->failed
	Status string `gorm:"type:varchar(20);default:'uploaded'" json:"status"` // 录音状态

	//关联,一对一关联分析结果
	AnalysisResult AnalysisResult `gorm:"foreignKey:VoiceRecordID" json:"analysis_result,omitempty"`
}
