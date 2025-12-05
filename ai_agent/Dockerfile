# 轻量级的 python-slim
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖 
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 安装 uv
# 直接从官方镜像复制 uv 二进制文件
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# --- 第三步：使用 uv 安装依赖 ---
COPY requirements.txt .

# --system: 直接装在系统 python 里，不创建 venv
# --index-url: 指定阿里云源加速
# uv pip install: uv 的 pip 接口，完全兼容 pip 语法
RUN uv pip install --system --no-cache -r requirements.txt --index-url https://mirrors.aliyun.com/pypi/simple/

# 复制项目代码
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]