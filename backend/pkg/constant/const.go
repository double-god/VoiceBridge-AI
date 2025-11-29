package constant
// Gin Context Keys (用于中间件和Handler之间传值)

const (
	// CtxUserID 用于存储当前登录用户的 ID 类型uint
	CtxUserID = "ctx_user_id"

	// CtxUsername 用于存储当前登录用户的用户名
	CtxUsername = "ctx_username"

	// CtxRole 用于存储当前登录用户的角色
	CtxRole = "ctx_user_role"
)


const (
	// TokenHeaderKey 前端请求头里的 Key
	TokenHeaderKey = "Authorization"
	// TokenPrefix Token 的前缀
	TokenPrefix = "Bearer "
)