#!/bin/bash
# 清理卡住的语音记录，解决 AI Agent 处理队列阻塞问题

echo "=========================================="
echo "  VoiceBridge AI - 清理卡住的任务"
echo "=========================================="
echo ""

# 检查数据库连接
if ! docker ps | grep -q "voicebridge_postgres"; then
    echo "❌ PostgreSQL 容器未运行"
    echo "   请先启动: docker compose up -d postgres"
    exit 1
fi

echo "🔍 检查卡住的任务..."
stuck_count=$(docker exec voicebridge_postgres psql -U nainong -d nainong -t -c \
    "SELECT COUNT(*) FROM voice_records WHERE status LIKE 'processing%';" | tr -d ' ')

if [ "$stuck_count" -eq 0 ]; then
    echo "✅ 没有发现卡住的任务"
else
    echo "⚠️  发现 $stuck_count 个卡住的任务"
    echo ""
    echo "卡住的记录："
    docker exec voicebridge_postgres psql -U nainong -d nainong -c \
        "SELECT id, user_id, status, created_at FROM voice_records WHERE status LIKE 'processing%' ORDER BY id;"
    
    echo ""
    read -p "是否将这些任务重置为 uploaded 状态？(y/N) " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🔄 重置任务状态..."
        docker exec voicebridge_postgres psql -U nainong -d nainong -c \
            "UPDATE voice_records SET status = 'uploaded' WHERE status LIKE 'processing%';"
        
        echo "✅ 已重置 $stuck_count 个任务"
        echo ""
        echo "💡 提示: 重启后端服务以触发处理"
        echo "   docker compose restart backend"
    else
        echo "❌ 取消操作"
    fi
fi

echo ""
echo "=========================================="
echo "📊 当前任务统计"
echo "=========================================="

docker exec voicebridge_postgres psql -U nainong -d nainong -c \
    "SELECT status, COUNT(*) as count FROM voice_records GROUP BY status ORDER BY status;"

echo ""
echo "=========================================="
echo "💡 提示:"
echo "  - 卡住的任务通常是因为 AI Agent 崩溃或超时"
echo "  - 建议定期运行此脚本清理"
echo "  - 如果问题频繁出现，检查 AI Agent 日志"
echo "=========================================="
