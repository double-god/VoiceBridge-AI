#!/bin/bash

# TTS代理配置指南
# ================

echo "🔍 检测你的代理配置..."
echo ""

# 方案1: 检查常见代理端口
echo "【方案1】 检查Windows主机代理是否运行"
echo "----------------------------------------"
echo "常见代理软件端口:"
echo "  - Clash: 7890 (HTTP)"
echo "  - V2Ray: 10809 (HTTP), 10808 (SOCKS)"
echo "  - SSR: 1080 (SOCKS)"
echo ""

# 检查Windows进程(如果是WSL)
if command -v netstat.exe &> /dev/null; then
    echo "正在检查Windows端口监听..."
    netstat.exe -ano | grep -E ":(7890|10809|10808|1080|7891)" | grep LISTENING || echo "  ❌ 未发现常见代理端口"
else
    echo "  ℹ️  无法检测Windows端口 (不在WSL环境?)"
fi

echo ""
echo "【方案2】 如果代理需要允许局域网连接"
echo "----------------------------------------"
echo "大多数代理软件需要开启'允许局域网连接'选项:"
echo ""
echo "Clash配置:"
echo "  1. 打开Clash"
echo "  2. 设置 -> 开启'Allow LAN'(允许局域网连接)"
echo "  3. 重启Clash"
echo ""
echo "V2Ray配置:"
echo "  1. 打开V2Ray客户端"
echo "  2. 参数设置 -> 本地监听 -> 允许来自局域网的连接"
echo ""

echo "【方案3】 测试代理连接"
echo "----------------------------------------"
echo "请在Windows PowerShell中运行:"
echo ""
echo "  # 检查7890端口是否监听"
echo "  netstat -ano | findstr :7890"
echo ""
echo "  # 测试代理是否可用"
echo "  curl -x http://127.0.0.1:7890 https://www.google.com"
echo ""

echo "【方案4】 临时解决方案 - 禁用TTS"
echo "----------------------------------------"
echo "如果暂时无法配置代理,可以跳过TTS阶段测试:"
echo ""
echo "修改 .env 文件:"
echo "  TTS_PROXY=  # 留空或注释掉"
echo ""
echo "然后检查LLM是否正确保持语言(英文→英文):"
echo "  docker compose logs ai_agent | grep 'refined_text'"
echo ""

echo "【当前配置】"
echo "----------------------------------------"
echo "TTS_PROXY=$(grep TTS_PROXY /home/haotang/VoiceBridgeAI/VoiceBridge-AI/.env | grep -v '^#')"
echo ""
echo "【下一步】"
echo "----------------------------------------"
echo "1. 确认Windows代理在7890端口运行并允许局域网连接"
echo "2. 或修改.env中的TTS_PROXY为你实际的代理地址"
echo "3. 或暂时注释掉TTS_PROXY,先验证LLM语言保持功能"
echo "4. 运行: docker compose restart ai_agent"
echo "5. 再次测试: python3 test_fixes.py"
