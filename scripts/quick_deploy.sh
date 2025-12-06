#!/bin/bash
set -e

echo "🚀 一键部署 CosyVoice TTS"
echo "================================"
echo ""

cd /home/haotang/VoiceBridgeAI/VoiceBridge-AI

echo "1️⃣  清理旧容器和镜像..."
docker compose stop ai_agent 2>/dev/null || true
docker compose rm -f ai_agent 2>/dev/null || true
docker rmi voicebridge-ai-ai_agent:latest 2>/dev/null || true

echo ""
echo "2️⃣  开始构建 (预计3-5分钟)..."
echo "   正在下载: PyTorch, ModelScope, Transformers..."
docker compose build ai_agent

if [ $? -ne 0 ]; then
    echo "❌ 构建失败"
    exit 1
fi

echo ""
echo "3️⃣  启动容器..."
docker compose up -d ai_agent

echo ""
echo "4️⃣  等待服务就绪..."
sleep 8

echo ""
echo "5️⃣  查看状态和日志..."
docker ps --filter name=ai_agent --format "{{.Names}}: {{.Status}}"
echo ""
docker logs voicebridge_ai_agent --tail 20 2>&1

echo ""
echo "================================"
echo "✅ 部署完成!"
echo ""
echo "🧪 测试命令:"
echo "   python3 test_asr_llm.py"
echo ""
