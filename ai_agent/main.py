from fastapi import FastAPI
from api.router import router

app = FastAPI(title="VoiceBridge AI Agent")

# 注册路由
app.include_router(router, prefix="/api/agent")


@app.get("/health")
def health_check():
    """健康检查端点"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
