#!/bin/bash

echo "🔧 CosyVoice TTS 自动部署脚本"
echo "========================================"
echo ""

# 检查是否在构建
if docker compose ps ai_agent 2>/dev/null | grep -q "ai_agent"; then
    echo "⚠️  检测到容器存在，先停止..."
    docker compose stop ai_agent
    docker compose rm -f ai_agent
fi

echo "📦 步骤1: 构建容器 (包含CosyVoice依赖)"
echo "   - 这需要 3-5 分钟"
echo "   - 正在下载 modelscope, datasets, transformers 等..."
echo ""

docker compose build ai_agent

if [ $? -ne 0 ]; then
    echo "❌ 构建失败！请检查错误信息"
    exit 1
fi

echo ""
echo "✅ 构建成功！"
echo ""

echo "🚀 步骤2: 启动容器"
docker compose up -d ai_agent

if [ $? -ne 0 ]; then
    echo "❌ 启动失败！"
    exit 1
fi

echo ""
echo "⏳ 步骤3: 等待服务就绪 (10秒)"
sleep 10

echo ""
echo "📊 步骤4: 检查状态"
docker ps --filter name=ai_agent --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "📝 查看日志 (最后15行):"
docker logs voicebridge_ai_agent --tail 15 2>&1

echo ""
echo "========================================"
echo "✅ 部署完成！"
echo ""
echo "📌 重要提示:"
echo "  1. TTS使用延迟加载 - 首次调用时才会下载CosyVoice模型(~3-5GB)"
echo "  2. 模型会缓存到 cosy_models volume，避免重复下载"
echo "  3. 如果看到 '[TTS] CosyVoice 服务已就绪' 说明启动成功"
echo ""
echo "🧪 测试命令:"
echo "  python3 test_asr_llm.py  # 测试ASR+LLM (不触发TTS)"
echo ""
echo "📖 查看完整日志:"
echo "  docker compose logs -f ai_agent"
echo ""
