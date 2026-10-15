from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


#二 2.创建请求和响应模型
    #规定用户上传文档 时候，允许提交什么
class DocumentCreate(BaseModel):
    filename: str

    #规定API返回数据时候 返回什么
class DocumentRead(BaseModel):
    #允许 Pydantic 从 ORM 对象的属性读取数据并生成响应？
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    status: str
    created_at: datetime


#定义更新文档时,客户端可以提交的数据格式
#可为None原因： 如果用户只想修改一个，那么 不可以没有传另一个 就把另一个置为空
# filename:str/None 修改时filename可为str或者None,=None表示客户端不提供这个字段时，默认取None
class DocumentUpdate(BaseModel):
    filename: str | None = Field(default=None, min_length=1, max_length=255)  # 文件名可以不传，但传入字符串时长度必须为 1～255
    status: str | None = Field(default=None, min_length=1, max_length=30)  # 状态可以不传，但传入字符串时长度必须为 1～30
        # # 注意：以上约束仍允许显式传入 null；后续可以再通过模型校验器禁止显式 null。


