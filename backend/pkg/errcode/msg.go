package errcode

// 错误码定义
const (
	Success       = 0
	ServerError   = 10001
	InvalidParams = 10002
	NotFound      = 10003

	//Auth 模块
	Unauthorized   = 20001 // 未登录
	TokenMalformed = 20002 // Token 乱码
	TokenExpired   = 20003 // Token 过期（新增这个专用码，更清晰）
	TokenInvalid   = 20008 // Token 无效（签名不对/结构错误、重新分配唯一码）
	// 新增：缺少 Token 与中间件使用的别名（保持中间件现有调用方式不变）
	TokenMissing = 20007 // 请求未携带 Token
	// 兼容中间件已有命名（它目前使用 ErrTokenMissing / ErrTokenInvalid 作为业务码）
	ErrTokenMissing   = TokenMissing
	ErrTokenInvalid   = TokenInvalid
	UserNotFound      = 20004 // 用户不存在
	PasswordIncorrect = 20005 // 密码错误
	UserExists        = 20006 // 注册重复

	//Voice 模块
	UploadFailed    = 30001
	FileFormatError = 30002
	FileTooLarge    = 30003
	RecordNotFound  = 30004
	AnalysisFailed  = 30005
)

//错误信息映射

var MsgFlags = map[int]string{
	// 通用错误
	Success:       "操作成功",
	ServerError:   "系统开了个小差，请稍后再试",
	InvalidParams: "提交的信息有误，请检查后再试",
	NotFound:      "找不到您请求的资源",

	// 用户相关
	Unauthorized:      "您还没有登录，请先登录",
	TokenMalformed:    "登录状态异常，请重新登录",
	TokenExpired:      "登录已过期，请重新登录",
	TokenInvalid:      "Token 无效，请重新登录",
	TokenMissing:      "请求未携带 Token，请登录后重试",
	UserNotFound:      "该账号不存在，请检查用户名",
	PasswordIncorrect: "账号或密码错误，请重试",
	UserExists:        "这个用户名已经被别人注册啦，换一个试试吧",

	// 录音相关
	UploadFailed:    "上传失败了，请检查网络后重试",
	FileFormatError: "抱歉，不支持这种格式的录音，请上传 .wav 或 .webm 文件",
	FileTooLarge:    "录音时间过长,请把时间控制在90s内",
	RecordNotFound:  "找不到这条录音记录，可能已经被删除了",
	AnalysisFailed:  "AI 正在休息，分析服务暂时不可用",
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
