from fastapi import APIRouter, Body, Depends, HTTPException
from sqlmodel import SQLModel, Field, select
from typing import Optional
from sqlalchemy.orm import Session as SASession
from pydantic import BaseModel, Field as PydanticField


class FastZdpRoleUserModel(SQLModel, table=True):
    """用户与角色关系模型"""
    id: Optional[int] = Field(default=None, primary_key=True)

    role_id: int = Field(nullable=False)
    role_name: str = Field(nullable=False)
    user_id: int = Field(nullable=False)
    user_name: str = Field(nullable=False)


class FastZdpRoleUserModelSchema(BaseModel):
    role_id: int = PydanticField(gt=0)
    role_name: str = PydanticField(min_length=3, max_length=36)
    user_id: int = PydanticField(gt=0)
    user_name: str = PydanticField(min_length=3, max_length=36)


def get_role_user_router(
        get_db,
        prefix="/fastzdp_roleauth",
):
    router = APIRouter(prefix=prefix, tags=["fastzdp_roleauth 角色与用户关系管理"])

    @router.post("/role_user/", summary="新增角色与用户关系")
    def add_role_user(
            schema: FastZdpRoleUserModelSchema,
            db: SASession = Depends(get_db),
    ):

        # 创建
        new_role_user = FastZdpRoleUserModel(
            role_id=schema.role_id,
            role_name=schema.role_name,
            user_id=schema.user_id,
            user_name=schema.user_name,
        )
        db.add(new_role_user)
        try:
            db.commit()
            db.refresh(new_role_user)
        except Exception as e:
            print(e)
            db.rollback()
            raise HTTPException(status_code=400, detail="新增角色与用户关系失败")

        return {"message": "新增角色与用户关系成功", "id": new_role_user.id}

    @router.get("/role_user/", summary="角色与用户关系查询")
    def get_role_user(
            page: int = 1,
            size: int = 20,
            role_id: Optional[int] = None,
            role_name: Optional[str] = None,
            user_id: Optional[int] = None,
            user_name: Optional[str] = None,
            db: SASession = Depends(get_db),
    ):
        """
        - page：第几页
        - size：每页数量
        - role_id：角色id，如果有，则查询角色ID对应的数据
        - role_name：角色名称，如果有，则查询角色名称对应的数据，是like模糊查询
        - user_id：用户id，如果有，则查询用户ID对应的数据
        - user_name：用户名称，如果有，则查询用户名称对应的数据，是like模糊查询
        """

        # 查询
        query = select(FastZdpRoleUserModel)
        # 根据关键字查询
        if role_id:
            query = query.where(FastZdpRoleUserModel.role_id == role_id)
        if user_id:
            query = query.where(FastZdpRoleUserModel.user_id == user_id)
        if role_name:
            query = query.where(FastZdpRoleUserModel.role_name.like(f"%{role_name}%"))
        if user_name:
            query = query.where(FastZdpRoleUserModel.user_name.like(f"%{user_name}%"))

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

    @router.get("/role_user/{id}/", summary="根据ID查询角色与用户关系")
    def get_role_user_id(
            id: int,
            db: SASession = Depends(get_db),
    ):
        role = db.exec(select(FastZdpRoleUserModel).where(FastZdpRoleUserModel.id == id)).first()
        if not role:
            raise HTTPException(status_code=404, detail="角色与用户关系不存在")
        return role

    @router.put("/role_user/{id}/", summary="根据ID修改角色与用户关系")
    def update_role_user_id(
            id: int,
            schema: FastZdpRoleUserModelSchema,
            db: SASession = Depends(get_db),
    ):
        role_user = db.exec(select(FastZdpRoleUserModel).where(FastZdpRoleUserModel.id == id)).first()
        if not role_user:
            raise HTTPException(status_code=404, detail="角色与用户关系不存在")

        role_user.role_id = schema.role_id
        role_user.role_name = schema.role_name
        role_user.user_id = schema.user_id
        role_user.user_name = schema.user_name

        db.add(role_user)

        try:
            db.commit()
            db.refresh(role_user)
        except Exception as e:
            print(e)
            db.rollback()
            raise HTTPException(status_code=400, detail="修改角色与用户关系失败")

        return role_user

    @router.delete("/role_user/{id}/", summary="根据ID删除角色与用户关系")
    def delete_role_id(
            id: int,
            db: SASession = Depends(get_db),
    ):
        role = db.exec(select(FastZdpRoleUserModel).where(FastZdpRoleUserModel.id == id)).first()
        if not role:
            raise HTTPException(status_code=404, detail="角色与用户关系不存在")
        db.delete(role)
        db.commit()
        return role

    return router
