# CosyVoice TTS 部署状态

## 当前状态

🔄 **正在构建容器** - 下载 CosyVoice 依赖包 (modelscope, datasets, transformers 等)

预计还需要 **2-3 分钟** 完成

## 已完成的配置

✅ **Dockerfile** - 添加了 CosyVoice 依赖包  
✅ **tts_cosy.py** - 使用延迟加载策略 (避免启动时导入错误)  
✅ **pipeline.py** - 已改为使用 `tts_cosy`  
✅ **docker-compose.yml** - 添加了 `cosy_models` volume

## 构建完成后的操作

```bash
# 1. 启动容器
docker compose up -d ai_agent

# 2. 查看日志确认启动
docker compose logs ai_agent --tail 20

# 应该看到: [TTS] CosyVoice 服务已就绪 (模型将在首次调用时加载)

# 3. 测试ASR+LLM (不触发TTS下载)
python3 test_asr_llm.py
```

## 关于模型下载

⚠️ **首次调用 TTS 时** 会自动下载 CosyVoice-300M-SFT 模型 (~3-5GB)

- 下载时间: 3-10 分钟 (取决于网速)
- 缓存位置: Docker volume `cosy_models`
- 只下载一次，后续重启不需要重新下载

## 测试流程

1. **先测试 ASR+LLM**: `python3 test_asr_llm.py`

   - 这个测试不会触发 TTS，验证语音识别和意图理解

2. **再测试完整流程** (包括 TTS):
   - 上传一个音频，等待处理完成
   - 首次会看到日志: `[TTS] 正在初始化 CosyVoice (首次运行会自动下载模型，约3-5GB)...`
   - 耐心等待模型下载完成

## 当前构建进度

正在下载 PyTorch + CUDA 相关包...

- nvidia-cudnn-cu12
- nvidia-cublas-cu12
- nvidia-nccl-cu12
- ... (还有其他 CUDA 库)

这些是为了支持 GPU 加速，即使你没有 GPU 也可以用 CPU 模式运行。

---

**请等待构建完成后再启动容器！**
