package model

import "gorm.io/gorm"

type AnalysisResult struct {
	gorm.Model
	VoiceRecordID uint `gorm:"uniqueIndex;not null" json:"voice_record_id"`

	//AI 推理数据
	AsrText     string  `gorm:"type:text" json:"asr_text"`     // 原始听写的文本
	RefinedText string  `gorm:"type:text" json:"refined_text"` // AI 修复后的意图
	Confidence  float64 `gorm:"type:float" json:"confidence"`  // 置信度 (0.0 - 1.0)

	// 决策结果
	// accept直接播报, boundary询问确认, reject拒识别
	Decision string `gorm:"type:varchar(20)" json:"decision"`

	// 响应文本 (根据decision生成的用户友好提示)
	ResponseText string `gorm:"type:text" json:"response_text"`

	// TTS 播报
	TtsAudioUrl string `gorm:"type:varchar(255)" json:"tts_audio_url"`
}
