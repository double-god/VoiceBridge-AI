#!/bin/bash

echo "=== TTS重构 - 快速诊断 ==="
echo ""

echo "【1】容器状态检查"
echo "---"
docker ps -a --filter name=ai_agent --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo "【2】最新日志 (最后20行)"
echo "---"
docker logs voicebridge_ai_agent --tail 20 2>&1 || echo "容器未运行或日志为空"
echo ""

echo "【3】如果看到错误,尝试重启"
echo "---"
echo "执行: docker compose restart ai_agent"
echo ""

echo "【4】查看完整日志"
echo "---"
echo "执行: docker compose logs -f ai_agent"
echo ""

echo "【5】进入容器检查环境"
echo "---"
echo "执行: docker compose exec ai_agent python3 -c 'import modelscope; print(modelscope.__version__)'"
