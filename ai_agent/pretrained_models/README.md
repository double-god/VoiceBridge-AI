# CosyVoice 预训练模型缓存目录

此目录用于存储 CosyVoice TTS 模型，避免容器重启时重复下载。

## 目录说明

此目录映射到容器内的 `/root/.cache/modelscope` 路径，ModelScope 会自动将下载的模型缓存到这里。

## 模型来源

- **模型库**: ModelScope (魔搭社区)
- **自动下载**: 首次运行时会自动从 ModelScope 下载所需模型
- **模型大小**: 约 3-5 GB

## 目录结构（首次运行后）

```
pretrained_models/
└── hub/
    └── iic/
        └── CosyVoice-300M/
            ├── campplus.onnx
            ├── speech_tokenizer_v1.onnx
            ├── speech_tokenizer_v2.onnx
            └── ...
```

## 注意事项

1. **不要手动删除**此目录中的文件，否则会触发重新下载
2. **磁盘空间**: 确保至少有 10 GB 可用空间
3. **网络要求**: 首次下载需要稳定的网络连接
4. **Git 忽略**: 此目录已添加到 `.gitignore`，不会提交到版本控制

## 清理缓存

如果需要清理模型缓存并重新下载：

```bash
# 停止服务
docker compose down

# 删除缓存
rm -rf ai_agent/pretrained_models/*

# 重新启动（会自动下载）
docker compose up -d
```

## 跨项目共享

如果你的机器上有多个项目使用 CosyVoice，可以将此目录软链接到统一的缓存位置：

```bash
# 创建统一缓存目录
mkdir -p ~/model_cache/modelscope

# 删除当前目录
rm -rf ai_agent/pretrained_models

# 创建软链接
ln -s ~/model_cache/modelscope ai_agent/pretrained_models
```
