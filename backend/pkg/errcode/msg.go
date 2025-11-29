package errcode

//业务错误码定义
const (
	Success       = 0
	ServerError   = 10001
	InvalidParams = 10002
	NotFound      = 10003

	// Auth 模块
	Unauthorized      = 20001 // 未登录
	TokenMalformed    = 20002 // Token 乱码
	TokenExpired      = 20003 // Token 过期
	UserNotFound      = 20004 // 用户不存在
	PasswordIncorrect = 20005 // 密码错误
	UserExists        = 20006 // 注册重复
	TokenMissing      = 20007 // 请求未携带 Token
	TokenInvalid      = 20008 // Token 无效

	// 兼容中间件的别名引用
	ErrTokenMissing = TokenMissing
	ErrTokenInvalid = TokenInvalid

	// Voice 模块
	UploadFailed    = 30001 // 上传失败
	FileFormatError = 30002 // 格式不支持
	FileTooLarge    = 30003 // 文件过大
	RecordNotFound  = 30004 // 找不到录音
	AnalysisFailed  = 30005 // AI 分析中途失败

	AgentTaskError = 40001 // 提交任务给 Python 失败
)



var MsgFlags = map[int]string{
	// 通用错误
	Success:       "操作成功",
	ServerError:   "系统稍微开了个小差，请稍后再试",
	InvalidParams: "提交的信息有些问题，请检查一下",
	NotFound:      "找不到您请求的内容",

	// 用户相关
	Unauthorized:      "您还没有登录，请先登录",
	TokenMalformed:    "登录状态异常，请重新登录试试",
	TokenExpired:      "登录已过期，为了安全请重新登录",
	TokenInvalid:      "登录信息无效，请重新登录",
	TokenMissing:      "您需要登录才能使用此功能",
	UserNotFound:      "该账号不存在，请检查用户名是否正确",
	PasswordIncorrect: "账号或密码不对，请重试",
	UserExists:        "这个用户名已经被别人注册啦，换一个试试吧",

	// 录音相关
	UploadFailed:    "上传失败了，请检查网络后重试",
	FileFormatError: "抱歉，暂不支持这种格式，请上传 .wav 或 .webm 录音",
	FileTooLarge:    "录音太长了，请控制在 90 秒以内",
	RecordNotFound:  "找不到这条录音记录，可能已经被删除了",
	AnalysisFailed:  "AI 分析服务暂时不可用，请稍后再试",

	// Agent 相关
	AgentTaskError: "任务提交失败,AI 助手可能正在休息",
}

// GetMsg 获取友好的错误提示
func GetMsg(code int) string {
	msg, ok := MsgFlags[code]
	if ok {
		return msg
	}
	// 如果遇到未定义的错误码，返回统一的友好提示
	return MsgFlags[ServerError]
}