from fastapi import APIRouter, Body, Depends, HTTPException
from sqlmodel import SQLModel, Field, select
from typing import Optional
from sqlalchemy.orm import Session as SASession


class FastZdpAuthModel(SQLModel, table=True):
    """用户权限模型"""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    nickname: str


def get_auth_router(
        get_db,
        prefix="/fastzdp_roleauth",
):
    router = APIRouter(prefix=prefix, tags=["fastzdp_roleauth 权限管理"])

    @router.post("/auth/", summary="新增权限")
    def add_auth(
            name: str = Body(str, min_length=2, max_length=36),
            nickname: str | None = Body(None),
            db: SASession = Depends(get_db),
    ):
        # 检查是否已存在
        auth = db.exec(select(FastZdpAuthModel).where(FastZdpAuthModel.name == name)).first()
        if auth:
            raise HTTPException(status_code=400, detail="权限名已存在")

        # 创建
        new_auth = FastZdpAuthModel(name=name, nickname=nickname)
        db.add(new_auth)
        try:
            db.commit()
            db.refresh(new_auth)
        except Exception as e:
            print(e)
            db.rollback()
            raise HTTPException(status_code=400, detail="新增权限失败")

        return {"message": "新增权限成功", "auth_id": new_auth.id}

    @router.get("/auth/", summary="权限查询")
    def get_auth(
            page: int = 1,
            size: int = 20,
            name: str = "",
            nickname: str = "",
            db: SASession = Depends(get_db),
    ):
        """
        分页查询权限
        """

        # 查询
        query = select(FastZdpAuthModel)
        # 根据关键字查询
        if name:
            query = query.where(FastZdpAuthModel.name.like(f"%{name}%"))
        if nickname:
            query = query.where(FastZdpAuthModel.nickname.like(f"%{nickname}%"))

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

    @router.get("/auth/{id}/", summary="根据ID查询权限")
    def get_auth_id(
            id: int,
            db: SASession = Depends(get_db),
    ):
        auth = db.exec(select(FastZdpAuthModel).where(FastZdpAuthModel.id == id)).first()
        if not auth:
            raise HTTPException(status_code=404, detail="权限不存在")
        return auth

    @router.put("/auth/{id}/", summary="根据ID修改权限")
    def update_auth_id(
            id: int,
            name: str = Body(str, min_length=2, max_length=36),
            nickname: str | None = Body(None),
            db: SASession = Depends(get_db),
    ):
        auth = db.exec(select(FastZdpAuthModel).where(FastZdpAuthModel.id == id)).first()
        if not auth:
            raise HTTPException(status_code=404, detail="权限不存在")

        if name and name != auth.name:
            tmp_auth = db.exec(select(FastZdpAuthModel).where(FastZdpAuthModel.name == name)).first()
            if tmp_auth:
                raise HTTPException(status_code=400, detail="权限名已存在")
            auth.name = name
        if nickname:
            auth.nickname = nickname

        db.add(auth)
        db.commit()
        db.refresh(auth)

        return auth

    @router.delete("/auth/{id}/", summary="根据ID删除权限")
    def delete_auth_id(
            id: int,
            db: SASession = Depends(get_db),
    ):
        auth = db.exec(select(FastZdpAuthModel).where(FastZdpAuthModel.id == id)).first()
        if not auth:
            raise HTTPException(status_code=404, detail="权限不存在")
        db.delete(auth)
        db.commit()
        return auth

    return router
