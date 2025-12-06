# TTS 服务重构完成报告

## 🎯 重构目标

将不稳定的 Edge-TTS (需要代理) 替换为阿里 CosyVoice 离线模型

## ✅ 已完成的修改

### 1. Dockerfile 改造 (`ai_agent/Dockerfile`)

```dockerfile
# 新增 CosyVoice 依赖包
RUN uv pip install --system --no-cache \
    modelscope \        # 阿里模型管理库
    torchaudio \        # 音频处理
    addict \            # 配置字典
    scipy \             # 科学计算
    librosa \           # 音频分析
    soundfile \         # 音频文件IO
    datasets \          # HuggingFace datasets
    transformers \      # Transformer模型
    --index-url https://mirrors.aliyun.com/pypi/simple/
```

### 2. 新增 TTS 服务代码 (`ai_agent/core/tts_cosy.py`)

**核心特性:**

- ✅ 使用 ModelScope + CosyVoice-300M-SFT 模型
- ✅ 单例模式 - 全局只初始化一次
- ✅ 自动 GPU/CPU 检测
- ✅ 模型缓存到 `/app/models` (挂载 volume 避免重复下载)
- ✅ 兼容旧的 `tts_edge()` 接口，无需修改外部调用代码

**关键方法:**

```python
class TTSService:
    def __init__(self):
        # 下载模型: iic/CosyVoice-300M-SFT (~3-5GB)
        # 初始化pipeline (GPU优先)

    async def synthesize(text: str, output_file: str) -> str:
        # 合成语音并保存为WAV文件
```

### 3. 更新业务代码 (`ai_agent/services/pipeline.py`)

```python
# 修改前: from core import tts_edge
# 修改后: from core import tts_cosy

# 调用保持不变
tts_local_path = await tts_cosy.tts_edge(refined_text, temp_dir)
```

### 4. 清理配置文件

**删除的代理相关配置:**

- ❌ `ai_agent/core/config.py` - 删除 `TTS_PROXY` 设置
- ❌ `.env` - 删除 `TTS_PROXY=http://host.docker.internal:15715`
- ❌ `docker-compose.yml` - 删除 `TTS_PROXY` 环境变量和 `extra_hosts`

**新增的持久化配置:**

```yaml
# docker-compose.yml
volumes:
  - cosy_models:/app/models  # 模型缓存卷

volumes:
  cosy_models:  # 定义volume
```

## 📦 构建状态

**当前:** 正在构建中 (下载 transformers, datasets 等大包)

**预计时间:**

- 构建: 2-5 分钟
- 首次运行下载模型: 3-10 分钟 (取决于网速)

## 🚀 使用指南

### 首次运行

```bash
# 1. 查看日志 (关注模型下载进度)
docker compose logs -f ai_agent

# 应该看到:
# [TTS] 正在初始化 CosyVoice (首次运行会自动下载模型，约3-5GB)...
# [TTS] 正在下载/加载模型: iic/CosyVoice-300M-SFT
# ... (模型下载中，可能需要几分钟)
# [TTS] ✅ CosyVoice 加载成功！运行设备: GPU/CPU
```

### 测试

```bash
# 测试ASR + LLM + TTS完整流程
python3 test_asr_llm.py
```

### 检查模型

```bash
# 查看已下载的模型文件
docker compose exec ai_agent ls -lh /app/models/

# 应该看到 CosyVoice-300M-SFT 目录
```

## ⚠️ 注意事项

### 显存要求

- **推荐**: 4GB+ 显存 (GPU 模式)
- **最低**: CPU 模式 (速度较慢，一句话约 5-10 秒)

### 首次运行慢的原因

1. **模型下载**: ~3-5GB (只下载一次，缓存在 volume)
2. **模型加载**: 加载到内存需要几十秒

### 网络配置

- ✅ **无需代理**: ModelScope 使用阿里云镜像
- ✅ **国内加速**: pip 使用阿里源 `mirrors.aliyun.com`

## 🔄 与 Edge-TTS 的对比

| 特性     | Edge-TTS    | CosyVoice       |
| -------- | ----------- | --------------- |
| 网络依赖 | ❌ 需要代理 | ✅ 国内直连     |
| 稳定性   | ❌ 经常超时 | ✅ 离线模型     |
| 音质     | 优秀        | 优秀            |
| 速度     | 快 (API)    | 中等 (本地推理) |
| 成本     | 免费但限制  | 完全离线免费    |
| 显存需求 | 无          | 3-4GB (GPU)     |

## 📝 后续优化建议

1. **GPU 支持**: 如需加速，确保 Docker 支持 CUDA
2. **模型选择**: 可尝试其他 CosyVoice 变种 (如 25M 轻量版)
3. **异步优化**: 当前 TTS 是阻塞的，可改为后台队列
4. **音色选择**: 目前用默认音色，可扩展支持多音色

## ✨ 优势总结

1. **彻底解决代理问题** - 无需配置 proxy、host.docker.internal 等
2. **生产环境友好** - 离线模型，不依赖外部 API
3. **接口兼容** - 无需修改外部调用代码
4. **模型可控** - 可自行 fine-tune 或更换模型

---

**状态**: ⏳ 等待构建完成 → 测试验证  
**预计完成时间**: 构建中 (5-10 分钟)
