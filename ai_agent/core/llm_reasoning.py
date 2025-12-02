import requests
import json
from .config import settings


def infer_intent(asr_text: str, user_profile: dict) -> dict:
    """
    Combine user profile for intent inference
    """
    # prompt design
    system_prompt = f"""
你是一个能与辅助构音障碍患者, 阿尔兹海默症患者, 认知障碍患者, 口齿不清的老年人沟通的AI专家. 任务是根据用户画像, 将模糊的语音(ASR文本)转换为明确的意图指令.

[用户画像]
- 姓名: {user_profile.get('name', '未知')}
- 年龄: {user_profile.get('age', '未知')}
- 健康状况: {user_profile.get('condition', '未知')}
- 习惯: {user_profile.get('habits', '未知')}
- 常见需求: {', '.join(user_profile.get('common_needs', []))}

[输出要求]
只允许返回json格式, 包含以下字段:
-refined_text: 修复后的文本(第一人称)
-confidence: 置信度(0-1之间的小数)
-decision: "accept"(>0.85), "boundary"(0.5-0.85), "reject"(<0.5).
- reason: 推理理由.
    """

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
