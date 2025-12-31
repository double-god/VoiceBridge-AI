# syntax=docker/dockerfile:1.4
# 启用 BuildKit 语法，支持高级缓存挂载

# ==========================================
# 阶段 1: Builder (构建环境)
# ==========================================
FROM python:3.11-slim-bookworm AS builder

WORKDIR /app

# 环境变量设置
ENV DEBIAN_FRONTEND=noninteractive \
    UV_HTTP_TIMEOUT=300 \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    # ✅ 关键修复：禁止 uv 下载 Python，强制使用系统 Python
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=python3.11

# 安装系统构建依赖
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    g++ \
    git \
    && apt-get clean

# 安装 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 复制项目依赖配置
COPY pyproject.toml uv.lock ./

# 同步依赖
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

# 安装 CosyVoice & Matcha-TTS (使用 ghfast.top 修复 + HTTP/1.1)
RUN --mount=type=cache,target=/root/.cache/git \
    git config --global http.version HTTP/1.1 && \
    GIT_SSL_NO_VERIFY=true git clone --depth 1 --single-branch https://ghfast.top/https://github.com/FunAudioLLM/CosyVoice.git /tmp/CosyVoice && \
    cp -r /tmp/CosyVoice/cosyvoice /app/.venv/lib/python3.11/site-packages/ && \
    rm -rf /tmp/CosyVoice && \
    GIT_SSL_NO_VERIFY=true git clone --depth 1 --single-branch https://ghfast.top/https://github.com/shivammehta25/Matcha-TTS.git /tmp/Matcha-TTS && \
    cp -r /tmp/Matcha-TTS/matcha /app/.venv/lib/python3.11/site-packages/ && \
    rm -rf /tmp/Matcha-TTS

# ==========================================
# 阶段 2: Runtime (生产环境)
# ==========================================
FROM python:3.11-slim-bookworm AS runtime

WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 安装运行时依赖
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 复制虚拟环境
COPY --from=builder /app/.venv /app/.venv

# 复制业务代码
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]