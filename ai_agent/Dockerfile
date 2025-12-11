# syntax=docker/dockerfile:1.4
# 启用 BuildKit 语法，支持缓存挂载

# 轻量级的 python-slim
FROM python:3.11-slim

WORKDIR /app

# ✅ 关键修改：设置非交互模式，防止 apt-get 等待用户输入
ENV DEBIAN_FRONTEND=noninteractive
# ✅ 增加 uv 的 HTTP 超时时间（国内网络优化）
ENV UV_HTTP_TIMEOUT=300

# ✅ 优化 apt 配置和安装命令
# - 使用阿里云镜像源加速下载
# - 使用 BuildKit 缓存挂载避免重复下载
# - 显式更新 ca-certificates 防止 SSL 错误
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    ffmpeg \
    git \
    g++ \
    build-essential \
    && apt-get clean

# 安装 uv
# 直接从官方镜像复制 uv 二进制文件
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 使用 uv 安装依赖
COPY requirements.txt .

# --system: 直接装在系统 python 里，不创建 venv
# --index-url: 指定阿里云源加速
# uv pip install: uv 的 pip 接口，完全兼容 pip 语法
# 使用 BuildKit 缓存挂载，多次构建时复用下载的包
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system -r requirements.txt --index-url https://mirrors.aliyun.com/pypi/simple/

# CosyVoice 依赖 (延迟导入，不会在启动时报错)
# 使用 BuildKit 缓存挂载，避免每次构建重新下载
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system \
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
# ✅ 使用 ghproxy.com 镜像加速 GitHub 访问（国内网络优化）
RUN git clone --depth 1 --single-branch \
    https://ghproxy.com/https://github.com/FunAudioLLM/CosyVoice.git /tmp/CosyVoice && \
    cp -r /tmp/CosyVoice/cosyvoice /usr/local/lib/python3.11/site-packages/ && \
    rm -rf /tmp/CosyVoice

# 安装 Matcha-TTS 子模块 (CosyVoice 依赖)
# ✅ 使用 ghproxy.com 镜像加速 GitHub 访问
RUN git clone --depth 1 --single-branch \
    https://ghproxy.com/https://github.com/shivammehta25/Matcha-TTS.git /tmp/Matcha-TTS && \
    cp -r /tmp/Matcha-TTS/matcha /usr/local/lib/python3.11/site-packages/ && \
    rm -rf /tmp/Matcha-TTS

# 安装 Matcha-TTS 和 CosyVoice 的 Python 依赖
# ✅ 使用 BuildKit 缓存挂载，避免每次构建重新下载
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system \
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