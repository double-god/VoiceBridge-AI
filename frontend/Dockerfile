# 使用 Node.js 官方轻量级镜像
FROM node:18-alpine

# 设置容器内的工作目录
WORKDIR /app

# 复制依赖定义文件 (package.json 和 lock 文件)
# 这样利用缓存，只有依赖变了才重新 npm install
COPY package*.json ./

# 安装依赖
RUN pnpm install

# 复制项目所有代码到容器里
COPY . .

# 暴露端口 (Vite 默认是 5173)
EXPOSE 5173

# 启动命令
# 注意：这里加了 -- --host 0.0.0.0
# 这是为了强制 Vite 监听所有网卡
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# 构建阶段
FROM node:18-alpine AS builder

WORKDIR /app

# 安装 pnpm
RUN npm install -g pnpm

# 复制 package.json 和 pnpm-lock.yaml
COPY package*.json pnpm-lock.yaml* ./

# 安装依赖
RUN pnpm install --frozen-lockfile

# 复制项目所有代码到容器里
COPY . .

# 构建生产版本
RUN pnpm build

# 生产阶段 - 使用 nginx 提供静态文件服务
FROM nginx:alpine

# 从构建阶段复制构建产物到 nginx 目录
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制 nginx 配置（用于前端路由支持）
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 启动 nginx
CMD ["nginx", "-g", "daemon off;"]