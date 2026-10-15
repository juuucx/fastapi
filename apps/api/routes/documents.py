
from typing import Annotated

from fastapi import APIRouter, Depends,HTTPException
from fastapi.openapi.utils import status_code_ranges
from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.db.session import get_db
from apps.schemas.document import DocumentCreate, DocumentRead, DocumentUpdate

from apps.models.document import Document
#
router=APIRouter(prefix="/documents",tags=["Documents"])

#作一个简单的名称转换
DbSession=Annotated[Session,Depends(get_db)]

@router.post("/",response_model=DocumentRead)
def create_document(
        # Pydantic校验请求
        data:DocumentCreate,
        db:DbSession
):
    #创建对象，
    document=Document(filename=data.filename)

    #把对象加入Session
    db.add(document)
    #db.commit 提交事务，保存记录
    db.commit()
    #刷新对象
    db.refresh(document)

    return document

@router.get("/",response_model=list[DocumentRead])
def list_documents(db: DbSession):
    statement = select(Document).order_by(Document.id)
    documents=db.scalar(statement).all()
    return documents

@router.get("/{document_id}",response_model=DocumentRead)
def get_document(
        document_id:int,
        db:DbSession,
):
    #在Document表里面按照document_id来查找
    document=db.get(Document,document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )
    return document

@router.put("/{document_id}", response_model=DocumentRead)  # 注册 PUT 接口，并规定成功响应的数据格式
def update_document(
        document_id:int,
        data:DocumentUpdate,
        db:DbSession,# !!! 注意不要将 ： 写成 =。写为=默认前端传送，：为
):
    document=db.get(Document,document_id)

    if document is None:
        raise HTTPException(status_code=404,detail="Document not found")  #---->错

    # 只提取客户端真正提交的字段，忽略没有提交的字段
    update_data=data.model_dump(exclude_unset=True)

    # 遍历客户端提交的每一个字段及其新值
    for field,value in update_data.items():
        # 把对应字段修改为新值，例如修改 document.filename
        setattr(document,field,value)

    db.commit()
    # 从数据库重新读取该对象，确保拿到最新数据：
    #如：如数据库有自动生成的字段，或者数据库会自动更新某些值时，刷新对象可以让程序拿到最新的数据。
    db.refresh(document)
    return document

@router.delete("/{document_id}")
def delete_document(
        document_id:int,
        db:DbSession,
):
    document=db.get(Document,document_id)

    if document is None:
        raise HTTPException(status_code=404,detail="文件未存在")  #-->错

    else:
        db.delete(document)
        db.commit()
    return {"message":"文件删除成功！"}

#==================以上进行测试==================
# 新增文档
# POST /documents/，提交 filename。
# [ ] 正常更新
# PUT /documents/1，只修改 filename，确认 status 保持不变。
# [ ] 更新不存在的文档
# PUT /documents/9999，预期 HTTP 404
# [ ] 正常删除
# DELETE /documents/1，预期返回成功消息。
# [ ] 重复删除
# 再次 DELETE /documents/1，预期 HTTP 404。
# [ ] 删除后查询
# GET /documents/1，预期 HTTP 404。

# =========！---以下需注意-----！=======
# 不仅测试“正常情况”，还测试了错误情况：
# - 正常情况：输入合法、数据存在，操作应该成功。
# - 异常情况：数据不存在，接口应该返回正确的错误码。
# - 状态一致性：删除后，再查询应该查不到。
# - 字段保持：更新文件名时，不应该意外修改其他字段。