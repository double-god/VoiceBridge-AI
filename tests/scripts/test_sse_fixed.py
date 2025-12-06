#!/usr/bin/env python3
"""
测试修复后的 SSE 连接 - 验证状态统一性
"""

import requests
import sys


def test_sse_with_completed_status():
    """测试 SSE 是否能正确识别 completed 状态"""

    # 1. 注册测试用户
    print("1. 注册测试用户...")
    resp = requests.post(
        "http://localhost:80/api/v1/auth/register",
        json={
            "username": "test_sse@example.com",
            "password": "Test123456",
            "nickname": "SSE测试用户",
        },
    )

    if resp.status_code == 200:
        data = resp.json()
        if data["code"] == 20000:
            token = data["data"]["token"]
            print(f"✅ 注册成功, Token: {token[:50]}...")
        else:
            print(f"注册失败: {data['msg']}")
            return
    else:
        print(f"❌ 请求失败: {resp.status_code}")
        return

    # 2. 测试 record 63 的 SSE
    print("\n2. 测试 SSE 连接 (record 63)...")
    resp = requests.get(
        "http://localhost:80/api/v1/voice/status/stream/63",
        headers={"Authorization": f"Bearer {token}"},
        stream=True,
        timeout=10,
    )

    print(f"Status: {resp.status_code}")
    print(f"Content-Type: {resp.headers.get('Content-Type')}")
    print("\n--- SSE Events ---")

    event_count = 0
    for line in resp.iter_lines(decode_unicode=True):
        if line:
            print(f"[{event_count}] {line}")
            event_count += 1

            # SSE 应该在发送 completed 状态后关闭连接
            if '"status":"completed"' in line or '"status": "completed"' in line:
                print("\n✅ 检测到 completed 状态, SSE 应该关闭连接")
                break

            if event_count > 5:
                print("\n❌ SSE 发送了超过 5 个事件, 可能没有正确终止")
                break

    print(f"\n总共接收 {event_count} 个事件")

    # 3. 测试获取历史记录
    print("\n3. 获取历史记录...")
    resp = requests.get(
        "http://localhost:80/api/v1/voice/history",
        headers={"Authorization": f"Bearer {token}"},
        params={"page": 1, "page_size": 10},
    )

    if resp.status_code == 200:
        data = resp.json()
        if data["code"] == 20000:
            records = data["data"]["records"]
            print(f"✅ 获取到 {len(records)} 条记录")

            for r in records[:3]:  # 只显示前3条
                print(f"\n  Record {r['id']}:")
                print(f"    Status: {r['status']}")
                print(f"    Refined: {r.get('refined_text', '')[:50]}")
                print(f"    TTS URL: {r.get('tts_url', 'N/A')}")
        else:
            print(f"❌ 获取失败: {data['msg']}")
    else:
        print(f"❌ 请求失败: {resp.status_code}")


if __name__ == "__main__":
    test_sse_with_completed_status()
