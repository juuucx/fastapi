from fastapi import FastAPI

from apps.db.base import Base
from apps.db.session import engine
from apps.api.routes.documents import router as documents_router

from apps.api.routes.llm import router as llm_router  # 导入新建的大模型路由

#  ！：项目启动阶段一次性完成数据库初始化，
#  **程序启动前准备好数据表**。等服务开始接收请求的时候，表已经准备好了，接口可以直接读写表。
Base.metadata.create_all(bind=engine)

#实例化
app = FastAPI(title="AI Quality Platform")
#挂在文档路由
app.include_router(documents_router)

app.include_router(llm_router)  # 将大模型路由注册到现有 FastAPI 应用


@app.get("/health")
def health_check():
    return {"status": "ok"}

