from fastapi import APIRouter, Body, Depends, HTTPException
from sqlmodel import SQLModel, Field, select
from typing import Optional
from sqlalchemy.orm import Session as SASession
from pydantic import BaseModel, Field as PydanticField


class FastZdpRoleAuthModel(SQLModel, table=True):
    """角色与权限关系模型"""
    id: Optional[int] = Field(default=None, primary_key=True)

    role_id: int = Field(nullable=False)
    role_name: str = Field(nullable=False)
    auth_id: int = Field(nullable=False)
    auth_name: str = Field(nullable=False)


class FastZdpRoleAuthModelSchema(BaseModel):
    role_id: int = PydanticField(gt=0)
    role_name: str = PydanticField(min_length=3, max_length=36)
    auth_id: int = PydanticField(gt=0)
    auth_name: str = PydanticField(min_length=3, max_length=36)


def get_role_auth_router(
        get_db,
        prefix="/fastzdp_roleauth",
):
    router = APIRouter(prefix=prefix, tags=["fastzdp_roleauth 角色与权限关系管理"])

    @router.post("/role_auth/", summary="新增角色与权限关系")
    def add_role_auth(
            schema: FastZdpRoleAuthModelSchema,
            db: SASession = Depends(get_db),
    ):

        # 创建
        new_role_auth = FastZdpRoleAuthModel(
            role_id=schema.role_id,
            role_name=schema.role_name,
            auth_id=schema.auth_id,
            auth_name=schema.auth_name,
        )
        db.add(new_role_auth)
        try:
            db.commit()
            db.refresh(new_role_auth)
        except Exception as e:
            print(e)
            db.rollback()
            raise HTTPException(status_code=400, detail="新增角色与权限关系失败")

        return {"message": "新增角色与权限关系成功", "id": new_role_auth.id}

    @router.get("/role_auth/", summary="角色与权限关系查询")
    def get_role_auth(
            page: int = 1,
            size: int = 20,
            role_id: Optional[int] = None,
            role_name: Optional[str] = None,
            auth_id: Optional[int] = None,
            auth_name: Optional[str] = None,
            db: SASession = Depends(get_db),
    ):
        """
        - page：第几页
        - size：每页数量
        - role_id：角色id，如果有，则查询角色ID对应的数据
        - role_name：角色名称，如果有，则查询角色名称对应的数据，是like模糊查询
        - auth_id：权限id，如果有，则查询权限ID对应的数据
        - auth_name：权限名称，如果有，则查询权限名称对应的数据，是like模糊查询
        """

        # 查询
        query = select(FastZdpRoleAuthModel)
        # 根据关键字查询
        if role_id:
            query = query.where(FastZdpRoleAuthModel.role_id == role_id)
        if auth_id:
            query = query.where(FastZdpRoleAuthModel.auth_id == auth_id)
        if role_name:
            query = query.where(FastZdpRoleAuthModel.role_name.like(f"%{role_name}%"))
        if auth_name:
            query = query.where(FastZdpRoleAuthModel.auth_name.like(f"%{auth_name}%"))

        # 统计总数
        total_count = len(db.exec(query).all())

        # 分页
        query = query.offset((page - 1) * size).limit(size)
        # 执行查询
        results = db.exec(query).all()
        # 返回
        return {
            "count": total_count,
            "data": results,
        }

    @router.get("/role_auth/{id}/", summary="根据ID查询角色与权限关系")
    def get_role_auth_id(
            id: int,
            db: SASession = Depends(get_db),
    ):
        role = db.exec(select(FastZdpRoleAuthModel).where(FastZdpRoleAuthModel.id == id)).first()
        if not role:
            raise HTTPException(status_code=404, detail="角色与权限关系不存在")
        return role

    @router.put("/role_auth/{id}/", summary="根据ID修改角色与权限关系")
    def update_role_auth_id(
            id: int,
            schema: FastZdpRoleAuthModelSchema,
            db: SASession = Depends(get_db),
    ):
        role_auth = db.exec(select(FastZdpRoleAuthModel).where(FastZdpRoleAuthModel.id == id)).first()
        if not role_auth:
            raise HTTPException(status_code=404, detail="角色与权限关系不存在")

        role_auth.role_id = schema.role_id
        role_auth.role_name = schema.role_name
        role_auth.auth_id = schema.auth_id
        role_auth.auth_name = schema.auth_name

        db.add(role_auth)

        try:
            db.commit()
            db.refresh(role_auth)
        except Exception as e:
            print(e)
            db.rollback()
            raise HTTPException(status_code=400, detail="修改角色与权限关系失败")

        return role_auth

    @router.delete("/role_auth/{id}/", summary="根据ID删除角色与权限关系")
    def delete_role_id(
            id: int,
            db: SASession = Depends(get_db),
    ):
        role = db.exec(select(FastZdpRoleAuthModel).where(FastZdpRoleAuthModel.id == id)).first()
        if not role:
            raise HTTPException(status_code=404, detail="角色与权限关系不存在")
        db.delete(role)
        db.commit()
        return role

    return router
