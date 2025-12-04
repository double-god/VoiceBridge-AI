# 构建阶段
FROM golang:1.25-alpine AS builder

WORKDIR /app

# 设置 Go 代理
ENV GOPROXY=https://goproxy.cn,direct

# 复制依赖文件
COPY go.mod go.sum ./
RUN go mod download

# 复制源码
COPY . .

# 编译
RUN CGO_ENABLED=0 GOOS=linux go build -o api_server cmd/api_server/main.go

# 运行阶段
FROM alpine:latest

WORKDIR /app

# 安装基础工具
RUN apk --no-cache add ca-certificates tzdata

# 复制二进制文件
COPY --from=builder /app/api_server .

# 暴露端口
EXPOSE 8080

# 启动命令
CMD ["./api_server"]
