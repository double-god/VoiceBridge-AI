#!/bin/bash

echo "🔄 正在重新构建 AI Agent (CosyVoice版本)..."
echo ""
echo "⚠️  注意事项:"
echo "  1. 首次构建会下载额外依赖包 (addict, scipy, librosa等)"
echo "  2. 构建时间约 2-5 分钟"
echo "  3. 首次运行时会自动下载 CosyVoice 模型 (~3-5GB)"
echo "  4. 模型会缓存到 cosy_models volume，避免重复下载"
echo ""
echo "开始构建..."
echo "========================================"

cd /home/haotang/VoiceBridgeAI/VoiceBridge-AI

# 构建
docker compose build ai_agent

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 构建成功!"
    echo ""
    echo "启动容器..."
    docker compose up -d ai_agent
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ 容器启动成功!"
        echo ""
        echo "📊 查看启动日志 (等待10秒)..."
        sleep 10
        docker compose logs ai_agent --tail 30
        
        echo ""
        echo "========================================"
        echo "🎯 下一步操作:"
        echo "========================================"
        echo ""
        echo "1. 查看完整日志 (关注 CosyVoice 初始化):"
        echo "   docker compose logs -f ai_agent"
        echo ""
        echo "2. 如果看到 '[TTS] 正在初始化 CosyVoice...':"
        echo "   - 首次运行会下载模型,需要等待3-10分钟"
        echo "   - 可以继续查看日志监控进度"
        echo ""
        echo "3. 等待看到 '[TTS] ✅ CosyVoice 加载成功!' 后:"
        echo "   python3 test_asr_llm.py  # 测试完整流程"
        echo ""
        echo "4. 检查模型下载进度:"
        echo "   docker compose exec ai_agent ls -lh /app/models/"
        echo ""
    else
        echo "❌ 容器启动失败"
        docker compose logs ai_agent --tail 50
    fi
else
    echo "❌ 构建失败,请检查错误信息"
fi
