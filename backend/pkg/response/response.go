//把响应结构体和响应方法封装到 response 包，统一管理 API 响应格式
package response

import (
	"net/http"

	"voicebridge/pkg/errcode"

	"github.com/gin-gonic/gin"
)

// Response 响应结构体
type Response struct {
	Code int         `json:"code"` // 业务码
	Msg  string      `json:"msg"`  // 提示信息
	Data interface{} `json:"data"` // 数据
}

// Success 成功响应
// data: 返回的具体数据结构
func Success(c *gin.Context, data interface{}) {
	c.JSON(http.StatusOK, Response{
		Code: errcode.Success, // 0
		Msg:  errcode.GetMsg(errcode.Success),
		Data: data,
	})
}

// Error 错误响应
// httpStatus控制网络层状态
// errCode如 10001, 20004 (控制业务层逻辑)
func Error(c *gin.Context, httpStatus int, errCode int) {
	c.JSON(httpStatus, Response{
		Code: errCode,
		Msg:  errcode.GetMsg(errCode), // 自动去 msg.go 查中文
		Data: nil,
	})
}

// ErrorWithMsg 错误响应
// 比如某些特殊场景下，想自定义错误提示信息
func ErrorWithMsg(c *gin.Context, httpStatus int, errCode int, msg string) {
	c.JSON(httpStatus, Response{
		Code: errCode,
		Msg:  msg,
		Data: nil,
	})
}