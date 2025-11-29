package repository

import (
	"errors"
	"voicebridge/internal/app/model"

	"gorm.io/gorm"
)

type UserRepo struct {
	db *gorm.DB
}

// newuserrepo构造函数
func NewUserRepo(db *gorm.DB) *UserRepo {
	return &UserRepo{db: db}
}

// create创建用户
func (r *UserRepo) Create(user *model.User) error {
	return r.db.Create(user).Error
}

// 根据用户名查询
func (r *UserRepo) FindByUsername(username string) (*model.User, error) {
	var user model.User
	//first会自动添加 limit 1
	err := r.db.Where("username = ?", username).First(&user).Error
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, nil // 用户不存在，返回nil
		}
		return nil, err // 其他错误

	}
	return &user, nil
}
func (r *UserRepo) Update(user *model.User, update map[string]interface{}) error {
	return r.db.Model(user).Updates(update).Error
}

// FindByID 根据ID查询用户
func (r *UserRepo) FindByID(id uint) (*model.User, error) {
	var user model.User
	err := r.db.First(&user, id).Error
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, nil
		}
		return nil, err
	}
	return &user, nil
}
