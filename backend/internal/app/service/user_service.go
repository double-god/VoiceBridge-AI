package service

import (
	"errors"
	"time"

	"voicebridge/internal/app/model"
	"voicebridge/internal/app/repository"
	"voicebridge/internal/pkg/config"
	"voicebridge/pkg/logger"
	"voicebridge/pkg/utils"

	"go.uber.org/zap"
	"golang.org/x/crypto/bcrypt"
)

type UserService struct {
	repo *repository.UserRepo
	cfg  *config.Config
}

func NewUserService(repo *repository.UserRepo, cfg *config.Config) *UserService {
	return &UserService{repo: repo, cfg: cfg}
}

// Register注册用户
func (s *UserService) Register(username, password string) (string, *model.User, error) {
	// 检查是否存在
	existUser, err := s.repo.FindByUsername(username)
	if err != nil {
		logger.Log.Error("查询用户失败", zap.Error(err))
		return "", nil, err
	}
	if existUser != nil {
		return "", nil, errors.New("user exists")
	}

	// 密码加密
	hash, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	if err != nil {
		logger.Log.Error("密码加密失败", zap.Error(err))
		return "", nil, err
	}

	// 构建并保存用户
	newUser := &model.User{
		Username: username,
		Password: string(hash),
		Role:     "patient",
	}

	if err := s.repo.Create(newUser); err != nil {
		logger.Log.Error("创建用户失败", zap.Error(err))
		return "", nil, err
	}

	// 注册成功后，直接签发 Token
	token, err := utils.GenerateToken(
		s.cfg.JWT.Secret,
		newUser.ID,
		newUser.Username,
		newUser.Role,
		24*7*time.Hour, // 7天过期
	)
	if err != nil {
		logger.Log.Error("Token签发失败", zap.Error(err))
		return "", nil, err
	}
	// 返回 Token 和 用户信息
	return token, newUser, nil
}

// 用户登录
func (s *UserService) Login(username, password string) (string, *model.User, error) {
	// 查找用户
	user, err := s.repo.FindByUsername(username)
	if err != nil {
		return "", nil, err
	}
	if user == nil {
		return "", nil, errors.New("user not found")
	}

	// 校验密码 (比较哈希)
	err = bcrypt.CompareHashAndPassword([]byte(user.Password), []byte(password))
	if err != nil {
		// 密码错误
		return "", nil, errors.New("password incorrect")
	}

	// 生成 JWT Token
	// 过期时间设为 14天
	token, err := utils.GenerateToken(
		s.cfg.JWT.Secret,
		user.ID,
		user.Username,
		user.Role,
		24*14*time.Hour,
	)
	if err != nil {
		logger.Log.Error("Token生成失败", zap.Error(err))
		return "", nil, err
	}

	return token, user, nil
}

// GetProfile获取画像
func (s *UserService) GetProfile(uid uint) (*model.User, error) {
	return s.repo.FindByID(uid)
}

// UpdateProfile更新画像
func (s *UserService) UpdateProfile(uid uint, req map[string]interface{}) error {
	// 先查出来，确保存在
	user, err := s.repo.FindByID(uid)
	if err != nil {
		return err
	}

	// 更新字段
	return s.repo.Update(user, req)
}
