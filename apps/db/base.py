from sqlalchemy.orm import DeclarativeBase


#2.创建ORM基类
    #项目所有数据库模型的共同基础 后面所有的orm模型都将继承Base
class Base(DeclarativeBase):
    pass