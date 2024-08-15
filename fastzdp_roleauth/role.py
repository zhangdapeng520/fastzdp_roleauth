from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlmodel import SQLModel, Field, select
from typing import Optional
from sqlalchemy.orm import Session as SASession


class FastZdpRoleModel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    nickname: str


def get_role_router(
        get_db,
        prefix="/fastzdp_roleauth",
):
    router = APIRouter(prefix=prefix, tags=["fastzdp_roleauth"])

    @router.post("/", summary="新增角色")
    def add_role(
            name: str = Body(str, min_length=2, max_length=36),
            nickname: str | None = Body(None),
            db: SASession = Depends(get_db),
    ):
        # 检查是否已存在
        role = db.exec(select(FastZdpRoleModel).where(FastZdpRoleModel.name == name)).first()
        if role:
            raise HTTPException(status_code=400, detail="角色名已存在")

        # 创建
        new_role = FastZdpRoleModel(name=name, nickname=nickname)
        db.add(new_role)
        try:
            db.commit()
            db.refresh(new_role)
        except Exception as e:
            print(e)
            db.rollback()
            raise HTTPException(status_code=400, detail="新增角色失败")

        return {"message": "新增角色成功", "role_id": new_role.id}

    @router.get("/", summary="角色查询")
    def get_role(
            page: int = 1,
            size: int = 20,
            name: str = "",
            nickname: str = "",
            db: SASession = Depends(get_db),
    ):
        """
        分页查询角色
        """

        # 查询
        query = select(FastZdpRoleModel)
        # 根据关键字查询
        if name:
            query = query.where(FastZdpRoleModel.name.like(f"%{name}%"))
        if nickname:
            query = query.where(FastZdpRoleModel.nickname.like(f"%{nickname}%"))

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

    @router.get("/{id}/", summary="根据ID查询角色")
    def get_role_id(
            id: int,
            db: SASession = Depends(get_db),
    ):
        role = db.exec(select(FastZdpRoleModel).where(FastZdpRoleModel.id == id)).first()
        if not role:
            raise HTTPException(status_code=404, detail="角色不存在")
        return role

    return router
