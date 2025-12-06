#!/usr/bin/env python3
"""
快速测试新上传是否正常工作
"""

import requests
import time
import json


def test_new_upload():
    """测试新上传和 SSE 进度"""

    # 1. 注册/登录
    print("1. 登录...")
    resp = requests.post(
        "http://localhost:80/api/v1/auth/register",
        json={
            "username": f"test_{int(time.time())}@example.com",
            "password": "Test123456",
            "nickname": "测试用户",
        },
    )

    if resp.status_code != 200:
        print(f"注册失败，尝试登录...")
        resp = requests.post(
            "http://localhost:80/api/v1/auth/login",
            json={"username": "test@example.com", "password": "Test123456"},
        )

    data = resp.json()
    if data["code"] != 20000:
        print(f"❌ 认证失败: {data['msg']}")
        return

    token = data["data"]["token"]
    print(f"✅ 认证成功")

    # 2. 上传测试音频
    print("\n2. 上传测试音频...")
    test_audio = b"\x00" * 1024  # 1KB 虚拟音频
    files = {"file": ("test.wav", test_audio, "audio/wav")}
    form_data = {"duration": "3000"}

    resp = requests.post(
        "http://localhost:80/api/v1/voice/upload",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
        data=form_data,
    )

    if resp.status_code != 200:
        print(f"❌ 上传失败: {resp.status_code} - {resp.text}")
        return

    upload_data = resp.json()
    if upload_data["code"] != 20000:
        print(f"❌ 上传失败: {upload_data['msg']}")
        return

    record_id = upload_data["data"]["id"]
    print(f"✅ 上传成功, record_id: {record_id}")

    # 3. 监听 SSE 进度
    print(f"\n3. 监听处理进度 (SSE)...")
    resp = requests.get(
        f"http://localhost:80/api/v1/voice/status/stream/{record_id}",
        headers={"Authorization": f"Bearer {token}"},
        stream=True,
        timeout=60,
    )

    progress_history = []
    for line in resp.iter_lines(decode_unicode=True):
        if line and line.startswith("data:"):
            try:
                event_data = json.loads(line[5:])
                status = event_data.get("status", "unknown")
                progress = event_data.get("progress", 0)

                progress_history.append((status, progress))
                print(f"  [{len(progress_history)}] {status}: {progress}%")

                # 检查是否完成
                if status in ["completed", "failed", "error", "cancelled"]:
                    print(
                        f"\n✅ 处理{'成功' if status == 'completed' else '失败'}: {status}"
                    )

                    if status == "completed":
                        print(f"  ASR: {event_data.get('asr_text', 'N/A')[:50]}")
                        print(
                            f"  Refined: {event_data.get('refined_text', 'N/A')[:50]}"
                        )
                        print(f"  TTS URL: {event_data.get('tts_url', 'N/A')}")
                        print(f"  Decision: {event_data.get('decision', 'N/A')}")
                    break

                if len(progress_history) > 50:
                    print("\n❌ SSE 循环超过 50 次,可能未正确终止!")
                    break

            except json.JSONDecodeError:
                continue

    # 4. 检查进度条是否正常递增
    print(f"\n4. 进度检查:")
    print(f"  总事件数: {len(progress_history)}")

    if progress_history:
        first_progress = progress_history[0][1]
        last_progress = progress_history[-1][1]
        print(f"  初始进度: {first_progress}%")
        print(f"  最终进度: {last_progress}%")

        # 检查是否有回退
        has_regression = False
        for i in range(1, len(progress_history)):
            if progress_history[i][1] < progress_history[i - 1][1]:
                print(
                    f"  ⚠️  进度回退: {progress_history[i-1][1]}% → {progress_history[i][1]}%"
                )
                has_regression = True

        if not has_regression:
            print(f"  ✅ 进度正常递增!")

        # 检查状态是否正确终止
        final_status = progress_history[-1][0]
        if final_status in ["completed", "failed", "error"]:
            print(f"  ✅ SSE 正确终止: {final_status}")
        else:
            print(f"  ❌ SSE 未正确终止,最终状态: {final_status}")


if __name__ == "__main__":
    test_new_upload()
