package repository

import (
	"voicebridge/internal/app/model"

	"gorm.io/gorm"
)

type VoiceRepo struct {
	db *gorm.DB
}

func NewVoiceRepo(db *gorm.DB) *VoiceRepo {
	return &VoiceRepo{db: db}
}

func (r *VoiceRepo) Create(record *model.VoiceRecord) error {
	return r.db.Create(record).Error
}

// 根据ID查询录音记录,prload加载关联的分析结果
func (r *VoiceRepo) FindByID(id uint) (*model.VoiceRecord, error) {
	var record model.VoiceRecord
	err := r.db.Preload("AnalysisResult").First(&record, id).Error
	return &record, err
}

// FindByUserID 分页查询历史记录
func (r *VoiceRepo) FindByUserID(userID uint, page, pageSize int) ([]model.VoiceRecord, int64, error) {
	var records []model.VoiceRecord
	var total int64

	// 统计总数
	query := r.db.Model(&model.VoiceRecord{}).Where("user_id = ?", userID)
	if err := query.Count(&total).Error; err != nil {
		return nil, 0, err
	}

	// 查询列表 (倒序)
	offset := (page - 1) * pageSize
	err := query.Order("created_at DESC").
		Limit(pageSize).
		Offset(offset).
		Preload("AnalysisResult"). // 关联查询结果
		Find(&records).Error

	return records, total, err
}

// UpdateStatus 更新状态 ，用于 Agent 回调或 SSE 轮询时状态变更
func (r *VoiceRepo) UpdateStatus(id uint, status string) error {
	return r.db.Model(&model.VoiceRecord{}).Where("id = ?", id).Update("status", status).Error
}

// Update 更新记录
func (r *VoiceRepo) Update(record *model.VoiceRecord) error {
	return r.db.Save(record).Error
}
