# VoiceBridge AI - 命令行操作指南

## 📦 1. 镜像打包

### 1.1 构建所有服务镜像

```bash
cd /home/haotang/VoiceBridgeAI/VoiceBridge-AI

# 构建所有服务（推荐：使用 BuildKit 缓存加速）
DOCKER_BUILDKIT=1 docker compose build

# 或者使用默认方式
docker compose build

# 查看构建结果
docker images | grep voicebridge
```

**性能优化说明**：

- ✅ Dockerfile 已启用 BuildKit 缓存挂载
- ✅ Python 依赖包会在多次构建间复用（避免重复下载）
- ✅ 首次构建需要下载 ~2GB 依赖（5-15 分钟）
- ✅ 后续构建只需 1-3 分钟（除非 requirements.txt 变化）

### 1.2 构建单个服务镜像

```bash
# 构建 AI Agent
docker compose build ai_agent

# 构建后端
docker compose build backend

# 构建前端
docker compose build frontend
```

### 1.3 强制重新构建（不使用缓存）

```bash
# 重新构建所有服务（⚠️ 会重新下载所有依赖，耗时较长）
docker compose build --no-cache

# 重新构建特定服务
docker compose build --no-cache ai_agent
```

**⚠️ 注意**：`--no-cache` 会清除 Docker 层缓存，但 BuildKit 缓存挂载仍会生效，所以依赖包不需要完全重新下载。

### 1.4 导出镜像（用于迁移/备份）

```bash
# 导出 AI Agent 镜像
docker save voicebridge-ai-ai_agent:latest -o voicebridge-ai-agent.tar

# 导出所有镜像
docker save \
  voicebridge-ai-ai_agent:latest \
  voicebridge-ai-backend:latest \
  voicebridge-ai-frontend:latest \
  -o voicebridge-all-images.tar

# 压缩导出
docker save voicebridge-ai-ai_agent:latest | gzip > voicebridge-ai-agent.tar.gz
```

### 1.5 导入镜像

```bash
# 在目标机器上导入
docker load -i voicebridge-ai-agent.tar

# 导入压缩包
gunzip -c voicebridge-ai-agent.tar.gz | docker load
```

### 1.6 推送到镜像仓库

```bash
# 登录 Docker Hub（如果使用）
docker login

# 打标签
docker tag voicebridge-ai-ai_agent:latest username/voicebridge-ai-agent:latest

# 推送
docker push username/voicebridge-ai-agent:latest
```

---

## 🧪 2. 运行测试数据

**⚠️ 重要提示：首次运行前请确保模型已下载完成**

```bash
# 检查模型状态（首次使用必做）
bash scripts/check_model_status.sh

# 或者查看实时下载进度
docker compose logs -f ai_agent
```

首次启动 AI Agent 会自动下载以下模型：

- **Whisper base** (~140MB) - 语音识别
- **CosyVoice-300M-SFT** (~2GB) - 语音合成

预计下载时间：5-15 分钟（取决于网速）。**下载完成前测试会超时！**

### 2.1 运行完整流程测试

```bash
cd /home/haotang/VoiceBridgeAI/VoiceBridge-AI

# 确保服务已启动且模型已下载
docker compose ps
bash scripts/check_model_status.sh

# 运行完整流程测试
python3 tests/scripts/test_full_pipeline.py
```

### 2.2 测试 ASR + LLM（不含 TTS）

```bash
# 快速测试 ASR 和 LLM 推理
python3 tests/scripts/test_asr_llm.py
```

### 2.3 测试 TTS 合成

```bash
# 单独测试 TTS 功能
python3 tests/scripts/test_tts.py
```

### 2.4 快速上传测试

```bash
# 测试文件上传和处理流程
python3 tests/scripts/test_upload_quick.py
```

### 2.5 运行演示数据集

```bash
# 进入 AI Agent 容器
docker exec -it voicebridge_ai_agent bash

# 运行演示数据
python3 run_dataset_demo.py

# 退出容器
exit
```

### 2.6 批量测试所有脚本

```bash
# 运行所有测试脚本
for test in tests/scripts/test_*.py; do
  echo "================================"
  echo "Running: $test"
  echo "================================"
  python3 "$test"
  echo ""
done
```

### 2.7 使用自定义音频测试

```bash
# 1. 准备音频文件（放到 ai_agent/data/demo/）
cp your_audio.wav ai_agent/data/demo/test_audio.wav

# 2. 修改测试脚本中的音频路径
# 编辑 tests/scripts/test_upload_quick.py

# 3. 运行测试
python3 tests/scripts/test_upload_quick.py
```

---

## 🚀 3. 启动整个服务

### 3.1 首次启动（完整流程）

```bash
cd /home/haotang/VoiceBridgeAI/VoiceBridge-AI

# 1. 检查环境变量配置
cat .env

# 2. 构建镜像
docker compose build

# 3. 启动所有服务
docker compose up -d

# 4. 查看服务状态
docker compose ps

# 5. 查看日志
docker compose logs -f
```

### 3.2 日常启动/停止

```bash
# 启动所有服务
docker compose up -d

# 停止所有服务
docker compose down

# 重启所有服务
docker compose restart

# 重启单个服务
docker compose restart ai_agent
```

### 3.3 查看服务状态

```bash
# 查看所有容器状态
docker compose ps

# 查看特定服务日志
docker compose logs -f ai_agent
docker compose logs -f backend
docker compose logs -f frontend

# 查看最近 100 行日志
docker compose logs --tail=100 ai_agent

# 实时查看所有服务日志
docker compose logs -f
```

### 3.4 启动特定服务

```bash
# 只启动数据库和存储
docker compose up -d postgres minio minio-init

# 启动后端服务
docker compose up -d backend

# 启动 AI Agent
docker compose up -d ai_agent

# 启动前端
docker compose up -d frontend nginx
```

### 3.5 完全清理并重新启动

```bash
# 停止并删除所有容器
docker compose down

# 删除数据卷（警告：会删除数据库数据）
docker compose down -v

# 删除镜像
docker compose down --rmi all

# 重新构建并启动
docker compose up --build -d
```

### 3.6 开发模式启动（不后台运行）

```bash
# 前台运行，查看实时日志
docker compose up

# 按 Ctrl+C 停止所有服务
```

### 3.7 热更新代码（不重启容器）

```bash
# AI Agent 代码已挂载，修改后自动生效（需重启服务）
docker compose restart ai_agent

# 后端代码需要重新构建
docker compose build backend && docker compose up -d backend

# 前端代码需要重新构建
docker compose build frontend && docker compose up -d frontend
```

---

## 🔍 4. 故障排查

### 4.1 检查容器健康状态

```bash
# 查看容器状态
docker compose ps

# 查看容器资源占用
docker stats

# 查看特定容器的详细信息
docker inspect voicebridge_ai_agent
```

### 4.2 进入容器调试

```bash
# 进入 AI Agent 容器
docker exec -it voicebridge_ai_agent bash

# 进入后端容器
docker exec -it voicebridge_backend sh

# 进入数据库容器
docker exec -it voicebridge_postgres psql -U nainong -d nainong
```

### 4.3 查看日志

```bash
# 查看 AI Agent 错误日志
docker compose logs ai_agent | grep -i error

# 查看所有服务的错误
docker compose logs | grep -i error

# 导出日志到文件
docker compose logs > service-logs.txt
```

### 4.4 检查网络连接

```bash
# 查看网络
docker network ls

# 查看容器 IP
docker inspect voicebridge_ai_agent | grep IPAddress

# 测试容器间连接
docker exec voicebridge_backend ping -c 3 ai_agent
```

### 4.5 清理未使用资源

```bash
# 清理停止的容器
docker container prune

# 清理未使用的镜像
docker image prune

# 清理未使用的卷
docker volume prune

# 清理所有未使用资源
docker system prune -a
```

---

## 📊 5. 数据库操作

### 5.1 连接数据库

```bash
# 连接 PostgreSQL
docker exec -it voicebridge_postgres psql -U nainong -d nainong
```

### 5.2 常用 SQL 查询

```sql
-- 查看所有表
\dt

-- 查看用户
SELECT id, username, name, age FROM users;

-- 查看最近 10 条语音记录
SELECT id, status, decision, created_at
FROM voice_records
ORDER BY id DESC
LIMIT 10;

-- 查看分析结果
SELECT id, decision, confidence,
       LEFT(asr_text, 50) as asr,
       LEFT(response_text, 50) as response
FROM analysis_results
ORDER BY id DESC
LIMIT 10;

-- 退出
\q
```

### 5.3 数据库备份与恢复

```bash
# 备份数据库
docker exec voicebridge_postgres pg_dump -U nainong nainong > backup.sql

# 恢复数据库
docker exec -i voicebridge_postgres psql -U nainong nainong < backup.sql
```

---

## 🗄️ 6. MinIO 存储操作

### 6.1 访问 MinIO 控制台

```
URL: http://localhost:9001
用户名: minioadmin
密码: 查看 .env 文件中的 MINIO_ROOT_PASSWORD
```

### 6.2 MinIO 命令行操作

```bash
# 使用 mc 客户端（需先安装）
docker exec voicebridge_minio mc ls voicebridge/

# 查看存储桶
docker exec voicebridge_minio mc ls
```

---

## 🔧 7. 快捷脚本

### 7.1 创建快捷启动脚本

```bash
# 创建 start.sh
cat > scripts/start.sh << 'EOF'
#!/bin/bash
cd /home/haotang/VoiceBridgeAI/VoiceBridge-AI
docker compose up -d
docker compose ps
echo "✅ 所有服务已启动"
echo "访问: http://localhost"
EOF

chmod +x scripts/start.sh
```

### 7.2 创建快捷停止脚本

```bash
# 创建 stop.sh
cat > scripts/stop.sh << 'EOF'
#!/bin/bash
cd /home/haotang/VoiceBridgeAI/VoiceBridge-AI
docker compose down
echo "✅ 所有服务已停止"
EOF

chmod +x scripts/stop.sh
```

### 7.3 创建日志查看脚本

```bash
# 创建 logs.sh
cat > scripts/logs.sh << 'EOF'
#!/bin/bash
cd /home/haotang/VoiceBridgeAI/VoiceBridge-AI
docker compose logs -f
EOF

chmod +x scripts/logs.sh
```

---

## 📝 8. 常用命令速查

```bash
# 启动服务
docker compose up -d

# 停止服务
docker compose down

# 查看状态
docker compose ps

# 查看日志
docker compose logs -f ai_agent

# 重启服务
docker compose restart ai_agent

# 重新构建
docker compose build ai_agent

# 进入容器
docker exec -it voicebridge_ai_agent bash

# 测试运行
python3 tests/scripts/test_upload_quick.py

# 数据库连接
docker exec -it voicebridge_postgres psql -U nainong -d nainong
```

---

## 🎯 9. 一键操作命令

### 完整重启流程

```bash
cd /home/haotang/VoiceBridgeAI/VoiceBridge-AI && \
docker compose down && \
docker compose build && \
docker compose up -d && \
docker compose ps
```

### 查看服务健康状态

```bash
cd /home/haotang/VoiceBridgeAI/VoiceBridge-AI && \
echo "=== 容器状态 ===" && \
docker compose ps && \
echo -e "\n=== AI Agent 日志 ===" && \
docker compose logs --tail=20 ai_agent
```

### 运行完整测试

```bash
cd /home/haotang/VoiceBridgeAI/VoiceBridge-AI && \
docker compose ps | grep -q "Up" && \
python3 tests/scripts/test_upload_quick.py || \
echo "请先启动服务: docker compose up -d"
```

---

**提示**:

- 所有命令都假设你在项目根目录 `/home/haotang/VoiceBridgeAI/VoiceBridge-AI`
- 使用 `cd /home/haotang/VoiceBridgeAI/VoiceBridge-AI` 切换到项目目录
- 查看更多帮助: `docker compose --help`
