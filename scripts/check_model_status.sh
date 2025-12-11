#!/bin/bash
# 检查 AI Agent 模型下载和加载状态

echo "=========================================="
echo "  VoiceBridge AI - 模型状态检查"
echo "=========================================="
echo ""

# 检查容器是否运行
echo "📦 检查容器状态..."
if ! docker ps | grep -q "voicebridge_ai_agent"; then
    echo "❌ AI Agent 容器未运行"
    echo "   启动命令: docker compose up -d ai_agent"
    exit 1
fi
echo "✅ AI Agent 容器正在运行"
echo ""

# 检查 API 健康状态
echo "🔍 检查 AI Agent API..."
if curl -s -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ API 服务正常响应"
else
    echo "⚠️  API 服务无响应（可能正在初始化）"
fi
echo ""

# 检查 Whisper 模型
echo "🎤 检查 Whisper 模型..."
if docker exec voicebridge_ai_agent ls /root/.cache/whisper/base.pt > /dev/null 2>&1; then
    size=$(docker exec voicebridge_ai_agent du -h /root/.cache/whisper/base.pt | cut -f1)
    echo "✅ Whisper 模型已下载 (大小: $size)"
else
    echo "⏳ Whisper 模型未下载"
fi
echo ""

# 检查 CosyVoice 模型
echo "🔊 检查 CosyVoice 模型..."
cosy_dir="/root/.cache/modelscope/iic/CosyVoice-300M-SFT"
if docker exec voicebridge_ai_agent test -d "$cosy_dir" 2>/dev/null; then
    echo "✅ CosyVoice 模型目录存在"
    
    # 检查关键模型文件
    files=("llm.pt" "flow.pt" "hift.pt" "speech_tokenizer_v1.onnx" "campplus.onnx")
    missing=0
    
    for file in "${files[@]}"; do
        if docker exec voicebridge_ai_agent test -f "$cosy_dir/$file" 2>/dev/null; then
            size=$(docker exec voicebridge_ai_agent du -h "$cosy_dir/$file" | cut -f1)
            echo "   ✓ $file ($size)"
        else
            echo "   ✗ $file (缺失)"
            missing=$((missing + 1))
        fi
    done
    
    if [ $missing -gt 0 ]; then
        echo "⚠️  CosyVoice 模型不完整，缺少 $missing 个文件"
    else
        echo "✅ CosyVoice 所有模型文件完整"
    fi
else
    echo "⏳ CosyVoice 模型未下载"
fi
echo ""

# 检查是否有正在下载的进程
echo "📥 检查下载进度..."
if docker compose logs ai_agent --tail=50 | grep -q "Downloading\|downloading"; then
    echo "⏳ 检测到正在下载，最近日志:"
    docker compose logs ai_agent --tail=20 | grep -E "Downloading|downloading|%"
else
    echo "✅ 没有检测到下载活动"
fi
echo ""

# 检查最近的错误
echo "🔍 检查最近错误..."
if docker compose logs ai_agent --tail=100 | grep -qi "error\|exception\|failed"; then
    echo "⚠️  发现错误日志:"
    docker compose logs ai_agent --tail=50 | grep -i "error\|exception\|failed" | tail -5
else
    echo "✅ 没有发现错误"
fi
echo ""

echo "=========================================="
echo "💡 提示:"
echo "  - 查看实时日志: docker compose logs -f ai_agent"
echo "  - 重启服务: docker compose restart ai_agent"
echo "  - 首次运行需要下载约 2GB 模型文件"
echo "=========================================="
