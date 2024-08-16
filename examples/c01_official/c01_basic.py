import fastzdp_roleauth
from fastapi import FastAPI
from sqlmodel import SQLModel, Field, create_engine, Session

# 创建数据库引擎
sqlite_url = "mysql+pymysql://root:root@127.0.0.1:3306/fastzdp_roleauth?charset=utf8mb4"
engine = create_engine(sqlite_url, echo=True)

# 确保表存在
# SQLModel.metadata.drop_all(engine)
SQLModel.metadata.create_all(engine)


def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()


app = FastAPI()

app.include_router(fastzdp_roleauth.get_role_router(get_db))  # 角色管理
app.include_router(fastzdp_roleauth.get_role_user_router(get_db))  # 角色与用户关系管理
app.include_router(fastzdp_roleauth.get_auth_router(get_db))  # 权限管理
app.include_router(fastzdp_roleauth.get_role_auth_router(get_db))  # 角色与权限管理

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8888)
