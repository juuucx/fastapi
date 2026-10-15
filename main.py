from datetime import datetime
from http.client import responses, HTTPException

from fastapi import FastAPI,Path,Query
from pydantic import BaseModel
from sqlalchemy import create_engine, func, DateTime, String,select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
from starlette.responses import FileResponse

from apps.db.session import DATABASE_URL, SessionLocal

app=FastAPI()

@app.get("/")
async def hello():
    return {"msg":"成功"}
#一、使用路由
@app.get("/user/hello")
async def hello():
    return {"msg":"我正在学习FastAPI"}

#路径参数：  对于限制 【在装饰器中使用 {} 即客户端需要输入的 （已被定义的参数）】
@app.get("/user/{id}")
async def test1(id:int):
    return {"id":id,
            "name":"普通用户id"}

#二、路径参数 ： 类型注解Path 限制长度、大小等,Path 是给【URL 路径里的参数】做校验
@app.get("/visiter/{id}")
async def visit1(id:int = Path(gt=0,lt=6,description='需要输入一个数字')):
    return{"id":id,
           "title":f'您是第{id}个访问者'}

@app.get("/visit/{id}/{name}")
async def visit1(
        id:int =Path(gt=0,le=100),
        name:str=Path(min_length=2,max_length=10)
):
    return {f'您是第{id}访问者，名字是{name}'}

#三、查询参数  post一般前端 进行 提交注册新增数据，不可在浏览器进行输入
@app.post("/question")
async def ask(
        ques:str=Query(default="怎么使用ai",min_length=5,max_length=256),
        price:int=Query(default="60",gt=50,le=100)
):
    return f'您的问题是{ques},此次询问价格为{price}'


#四： 请求体参数：创建、更新资源, post后 一同检测 是否符合语法 ;
    #Field 是给【Pydantic 模型类（BaseModel）里面的字段】做校验。
class User(BaseModel):
    username:str
    password:str

@app.post("/register")
async def register(user:User):
    return user

#  设计接口 新增图书，图书信息包含书名、作者、出版社、售价
from pydantic import Field
class Book(BaseModel):
    # 必填，字符串长度2~20，不写default就是不能为空
    book_name: str = Field(gt=2, le=20)
    # 必填，字符串长度2~10
    author: str = Field(gt=2, le=10)
    # 选填，不传就用默认值：黑马出版社
    pulisher: str = Field(default="黑马出版社")
    # 必填，数字大于0
    sales: int = Field(gt=0)

@app.get('/addbook')
async def add_book(book: Book):
    return book

#五：响应类型：默认为json 可设置为其他格式
    #1.整体返回，装饰器中设置
from fastapi.responses import HTMLResponse
@app.get("/html",response_class=HTMLResponse)
async def get_html():
    return "<h1>这是一级标题</h1>"

    #2.返回file类型
        #例子：返回图片格式
@app.get("/file")
async def get_jpg():
    path="jpgs/img.png"
    return FileResponse(path)

    #3.自定义相应数据格式  通过在装饰器中添加respons_model设置为自己定义的class
from pydantic import BaseModel
class News(BaseModel):
    id:int
    title:str
    content:str

@app.get("/News/{id}",response_model=News)
async def getnews(id:int=Path(gt=0)):
    return {
        "id": id,
        "title": f"新闻标题{id}",
        "content": f"这是第{id}条新闻的内容"
    }

#六：异常处理 终端正常处理流程
from fastapi.exceptions import HTTPException
@app.get('/get_ask/{id}')
async def get_ask(id:int=Path(gt=0)):
    ID=[1,2,3,4]
    if id not in ID:
        raise HTTPException(status_code=202,detail="输入错误")
    else:
        return {f'您输入的{id}正确'}



#========================进阶=======================
#七：中间件：为每个请求添加统一的处理逻辑（记录日志，身份认证，跨越，设置响应头，性能监控等）
# 定义：函数顶部使用装饰器
@app.middleware("http")
async def middleware1(request,call_next):
    print(f'中间件1 ---Start----')
    response=await call_next(request)
    print(f'中间件1 ----End----')
    return response

@app.middleware("http")
async def middleware2(request,call_next):
    print(f'中间件2 ---Start----')
    response=await call_next(request)
    print(f'中间件2 ----End----')
    return response

#八：依赖注入：使用依赖注入系统，来共享通用逻辑，便面代码重复 （是否使用 程序员说的算 ）
    #1.创建依赖项：封装共享代码
    #2.导入依赖depends
    #3.声明依赖项
    #与中间件不同：中间件只要写明，大家都跑，
from fastapi import Depends  #导入依赖

async def common_section():  #封装
    return {"开始跑共享代码"}

@app.get('/test')
async def test02(commons=Depends(common_section)):
    return commons



#1.建立数据库引擎（连接）
DATABASE_URL="sqlite:///./test_database.db"
test_engine=create_engine(
    DATABASE_URL,
)

SessionLocal=sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)

#2.定义基础类
class Base(DeclarativeBase):
    create_time:Mapped[datetime] = mapped_column(
        DateTime,
        insert_default=func.now(),
        nullable=False,
    )
#3.定义模型类
class Book(Base):
    __tablename__ = "books"

    id:Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )
    bookname:Mapped[str] =mapped_column(
        String(255),
        nullable=False,
    )

#4.启动应用时候创建 数据库表

def create_tables():
    Base.metadata.create_all(bind=test_engine)

@app.on_event("startup")
def startup_event():
    create_tables()

#以上可以成功建立 数据表
#5.根据路由查询 图书--> 使用get方法。此时没以恶搞获取，请求的方法只要涉及到数据库都需要建立数据库依赖，即都跑一下数据库

#5.1创建数据库依赖：
#把创建会话 关闭会话 单独封装起来
def database_insert():
    with SessionLocal() as session:
        try:
            yield session  #交给调用方，也就是交给db
        finally:
            session.close()

@app.get("/books/book")
def get_books(db=Depends(database_insert)):
    result = db.execute(select(Book))
    book=result.scalars().all()
    return book

#5.2
class bookcheck(BaseModel):
    id:int
    bookname:str

# ！：book:Book 对应的Book应该是pydantic检查
@app.post("/book/add_book")
def add_book(book:bookcheck,db=Depends(database_insert)):
    book_obj=Book(**book.__dict__)
    db.add(book_obj)
    db.commit()
    return book





