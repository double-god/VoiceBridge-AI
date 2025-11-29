package utils

//负责生成和解析 Token

import (
	"errors"
	"time"

	"github.com/golang-jwt/jwt/v5"
)

type MyCustomClaims struct {
	UserID   uint   `json:"uid"`
	Username string `json:"username"`
	Role     string `json:"role"`
	jwt.RegisteredClaims
}

// 生成JWT Token
// secret: 用于签名的密钥,从config传入
// expireDuration: token过期时间
// GenerateToken 生成带有自定义声明的 JWT Token
// 这里保持原接口，并新增对传入参数的最小检查（不改变现有调用方式）
func GenerateToken(secret string, userID uint, username, role string, expireDuration time.Duration) (string, error) {
	if secret == "" {
		return "", errors.New("jwt secret empty")
	}
	claims := MyCustomClaims{
		UserID:   userID,
		Username: username,
		Role:     role,
		RegisteredClaims: jwt.RegisteredClaims{
			ExpiresAt: jwt.NewNumericDate(time.Now().Add(expireDuration)),
			Issuer:    "voicebridge",
			IssuedAt:  jwt.NewNumericDate(time.Now()),
		},
	}

	//使用HS256算法生成token
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString([]byte(secret))
}

// 解析jwt token
// ParseToken 解析并返回自定义声明
func ParseToken(secret, tokenString string) (*MyCustomClaims, error) {
	token, err := jwt.ParseWithClaims(tokenString, &MyCustomClaims{}, func(token *jwt.Token) (interface{}, error) {
		return []byte(secret), nil
	})

	if err != nil {
		return nil, err
	}

	// 验证 token 是否有效
	if claims, ok := token.Claims.(*MyCustomClaims); ok && token.Valid {
		return claims, nil
	}

	return nil, errors.New("invalid token")
}
