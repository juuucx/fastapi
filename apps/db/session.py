
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL="sqlite:///./ai_quality.db"

#  1.创建数据库连接
    #数据库大门
engine =create_engine(
    #告诉 SQLAlchemy 使用 SQLite，并将数据库文件命名为 ai_quality.db
    DATABASE_URL,
    #SQLite 配合 FastAPI 常见的连接配置，用于允许数据库连接跨线程使用？
    connect_args={"check_same_thread":False},
)
    #sessionmaker相当于工厂，sessionLocal相当于产品模板。
    #操作数据库时候，调用sessionLocal 创建会话
SessionLocal = sessionmaker(
    #会话全都连接（bind）在engine这个数据库上
    bind=engine,
    #关闭自动提交，必须手动db.commit() 输入数据库，更加安全
    autocommit=False,
    #关闭自动刷新，避免不必要的数据库查询？
    autoflush=False

    #以上 只是创建了 Engine 和 Session 工厂，还没有创建任何数据库表。
)

#二、把ORM接入FastAPI
#1.创建数据库Session依赖

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

