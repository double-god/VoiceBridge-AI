import requests
import json
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

## 示例

输入: "那个...水...喝"
输出: {{"refined_text": "我想喝水", "confidence": 0.92, "decision": "accept", "reason": "用户表达了喝水的需求, 语义清晰"}}

输入: "药...吃了吗...早上"
输出: {{"refined_text": "我早上的药吃了吗?", "confidence": 0.78, "decision": "boundary", "reason": "用户询问用药情况, 但不确定是在问自己还是提醒"}}

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
    Combine user profile for intent inference
    """
    system_prompt = _build_system_prompt(user_profile)

    try:
        headers = {
            "Authorization": f"Bearer {settings.AI_AGENT_LLM_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "qwen3-max",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"ASR文本: {asr_text}"},
            ],
            "response_format": {"type": "json_object"},
        }

        resp = requests.post(
            settings.AI_AGENT_LLM_API_URL, headers=headers, json=payload
        )
        resp.raise_for_status()

        content = resp.json()["choices"][0]["message"]["content"]
        result = json.loads(content)

    except Exception as e:
        print(f"[LLM推理] 请求失败: {e}")
        # 降级处理
        result = {
            "refined_text": asr_text,
            "confidence": 0.0,
            "decision": "reject",
            "reason": f"推理服务不可用: {e}",
        }

    return result
