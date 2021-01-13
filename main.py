from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse

from internal import admin
from routers import items, users

from db.data_base import DataBaseModel, engine
from auth.handler import get_admin_token

DataBaseModel.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(users.router)
app.include_router(items.router)
app.include_router(
    admin.router,
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_admin_token)],
    responses={418: {"description": "I'm a teapot"}},
)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, log_level="info")
