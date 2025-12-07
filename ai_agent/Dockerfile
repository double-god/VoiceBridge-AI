# 轻量级的 python-slim
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖 (包含 CosyVoice 编译需要的工具)
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    g++ \
    build-essential \
    && rm -rf /var/lib/apt/lists/*
    # 清理 apt 缓存，减小镜像体积

# 安装 uv
# 直接从官方镜像复制 uv 二进制文件
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 使用 uv 安装依赖
COPY requirements.txt .

# --system: 直接装在系统 python 里，不创建 venv
# --index-url: 指定阿里云源加速
# uv pip install: uv 的 pip 接口，完全兼容 pip 语法
RUN uv pip install --system --no-cache -r requirements.txt --index-url https://mirrors.aliyun.com/pypi/simple/

# 🔥 CosyVoice 依赖 (延迟导入，不会在启动时报错)
RUN uv pip install --system --no-cache \
    modelscope \
    torchaudio \
    addict \
    scipy \
    librosa \
    soundfile \
    'datasets<3.0.0' \
    transformers \
    Pillow \
    simplejson \
    sortedcontainers \
    oss2 \
    yapf \
    einops \
    timm \
    conformer==0.3.2 \
    HyperPyYAML==1.2.2 \
    inflect==7.3.1 \
    hydra-core==1.3.2 \
    omegaconf==2.3.0 \
    protobuf==4.25 \
    pyworld==0.3.4 \
    'onnxruntime>=1.23.0' \
    wetext==0.0.4 \
    --index-url https://mirrors.aliyun.com/pypi/simple/

# 克隆并安装 CosyVoice
RUN git clone --depth 1 https://github.com/FunAudioLLM/CosyVoice.git /tmp/CosyVoice && \
    cp -r /tmp/CosyVoice/cosyvoice /usr/local/lib/python3.11/site-packages/ && \
    rm -rf /tmp/CosyVoice

# 安装 Matcha-TTS 子模块 (CosyVoice 依赖)
RUN git clone --depth 1 https://github.com/shivammehta25/Matcha-TTS.git /tmp/Matcha-TTS && \
# depth1 克隆只拿最新提交，减小镜像体积
    cp -r /tmp/Matcha-TTS/matcha /usr/local/lib/python3.11/site-packages/ && \
    # 直接把源码丢到 site-packages 里，省去安装步骤
    rm -rf /tmp/Matcha-TTS

# 安装 Matcha-TTS 和 CosyVoice 的 Python 依赖
RUN uv pip install --system --no-cache \
    diffusers \
    lightning \
    rich \
    matplotlib \
    gdown \
    hydra-colorlog \
    hydra-optuna-sweeper \
    rootutils \
    phonemizer \
    pytest \
    tensorboard \
    Cython \
    wandb \
    wget \
    torchcodec \
    --index-url https://mirrors.aliyun.com/pypi/simple/

# 复制项目代码
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]