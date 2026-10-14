
from fastapi import FastAPI,Path,Query
from pydantic import BaseModel

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

#二、路径参数 ： 类型注解Path 限制长度、大小等
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


#四： 请求体参数：创建、更新资源, post后 一同检测 是否符合语法
class User(BaseModel):
    username:str
    password:str

@app.post("/register")
async def register(user:User):
    return user

#五：响应类型：默认为json 可设置为其他格式
    #1.整体返回，装饰器中设置
from fastapi.responses import HTMLResponse
@app.get(path="/html",response_class=HTMLResponse)
async def get_html():
    return "<h1>这是一级标题</h1>"

    #2.返回file类型
        #例子：返回图片格式
@app.get("/jpg")
async def get_jpg():
    path=""





