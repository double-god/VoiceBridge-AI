import requests
import json
import time
from .config import settings


def _build_system_prompt(user_profile: dict) -> str:
    """
    Build system prompt with user profile and few-shot examples
    """
    common_needs = user_profile.get("common_needs", [])
    common_needs_str = ", ".join(common_needs) if common_needs else "无"

    return f"""你是一个专业的语音助手, 专门帮助构音障碍患者、阿尔兹海默症患者、认知障碍患者以及口齿不清的老年人进行沟通.

## 你的任务
将模糊的语音识别文本(ASR)转换为清晰、明确的意图表达, 并以第一人称输出.
**重要: 保持输入语言不变(中文输入→中文输出, 英文输入→英文输出).**

## 当前用户画像
- 姓名: {user_profile.get('name', '未知')}
- 年龄: {user_profile.get('age', '未知')}
- 健康状况: {user_profile.get('condition', '未知')}
- 日常习惯: {user_profile.get('habits', '未知')}
- 常见需求: {common_needs_str}

## 判断规则
- accept (confidence > 0.85): 意图清晰, 可以直接执行
- boundary (confidence 0.5-0.85): 意图大致明确但需确认
- reject (confidence < 0.5): 无法理解或完全无意义

## 重要提示
1. 优先匹配用户的"常见需求"列表
2. 结合用户的健康状况和日常习惯进行推理
3. 输出的 refined_text 必须是第一人称陈述句
4. 如果完全无法理解, 返回原文并标记 reject

## 示例 (中文)

输入: "那个...水...喝"
输出: {{"refined_text": "我想喝水", "confidence": 0.92, "decision": "accept", "reason": "用户表达了喝水的需求, 语义清晰"}}

输入: "药...吃了吗...早上"
输出: {{"refined_text": "我早上的药吃了吗?", "confidence": 0.78, "decision": "boundary", "reason": "用户询问用药情况, 但不确定是在问自己还是提醒"}}

## 示例 (English)

Input: "I need... water... drink"
Output: {{"refined_text": "I want to drink water", "confidence": 0.90, "decision": "accept", "reason": "User clearly expresses the need for water"}}

Input: "uh... medicine... morning"
Output: {{"refined_text": "Did I take my morning medicine?", "confidence": 0.75, "decision": "boundary", "reason": "User asking about medication, but context unclear"}}

## 无意义输入

输入: "嗯嗯啊啊呃"
输出: {{"refined_text": "嗯嗯啊啊呃", "confidence": 0.15, "decision": "reject", "reason": "无法识别有效语义内容"}}

## 输出格式
严格返回 JSON, 包含以下字段:
- refined_text: string, 修复后的文本(第一人称)
- confidence: number, 置信度(0-1)
- decision: string, "accept" | "boundary" | "reject"
- reason: string, 推理理由"""


def infer_intent(asr_text: str, user_profile: dict) -> dict:
    """
    Combine user profile for intent inference (with retry)
    """
    system_prompt = _build_system_prompt(user_profile)

    headers = {
        "Authorization": f"Bearer {settings.AI_AGENT_LLM_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.LLM_MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"ASR文本: {asr_text}"},
        ],
        "response_format": {"type": "json_object"},
    }

    # 重试机制: 最多3次, 指数退避
    max_retries = 3
    for attempt in range(max_retries):
        try:
            resp = requests.post(
                settings.AI_AGENT_LLM_API_URL, headers=headers, json=payload, timeout=30
            )
            resp.raise_for_status()

            content = resp.json()["choices"][0]["message"]["content"]
            result = json.loads(content)
            print(f"[Pipeline] LLM 结果: {result}")

            # 根据决策类型生成响应文本
            decision = result.get("decision", "reject")
            refined_text = result.get("refined_text", asr_text)

            if decision == "boundary":
                # boundary: 生成确认问句
                result["response_text"] = f"您想表达的意思是否为：{refined_text}？"
            elif decision == "reject":
                # reject: 生成道歉提示
                result["response_text"] = (
                    "抱歉，我不理解您说的话。您可以换一种方式再说一遍吗？"
                )
            elif decision == "accept":
                # accept: 使用精炼后的文本作为确认
                result["response_text"] = f"好的，{refined_text}"
            else:
                # 未知决策类型
                result["response_text"] = refined_text

            return result

        except (
            requests.exceptions.RequestException,
            requests.exceptions.SSLError,
            requests.exceptions.ConnectionError,
        ) as e:
            # 网络相关错误, 可重试
            if attempt < max_retries - 1:
                wait_time = 2**attempt  # 指数退避: 1s, 2s, 4s
                print(f"[LLM推理] 请求失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                print(f"[LLM推理] {wait_time}秒后重试...")
                time.sleep(wait_time)
                continue
            else:
                print(f"[LLM推理] 最终失败: {e}")
                return {
                    "refined_text": asr_text,
                    "confidence": 0.0,
                    "decision": "reject",
                    "reason": f"推理服务不可用(重试{max_retries}次后失败): {e}",
                    "response_text": "抱歉，语音服务暂时不可用，请稍后再试。",
                }

        except Exception as e:
            # 其他错误(如JSON解析), 不重试
            print(f"[LLM推理] 处理失败: {e}")
            return {
                "refined_text": asr_text,
                "confidence": 0.0,
                "decision": "reject",
                "reason": f"推理处理失败: {e}",
                "response_text": "抱歉，处理您的请求时出现错误。",
            }
