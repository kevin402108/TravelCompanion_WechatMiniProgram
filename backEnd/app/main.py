from fastapi import FastAPI
from backEnd.app.routers.db_router import db_router
from backEnd.app.routers.login_router import login_router
from backEnd.app.routers.user_router import user_router
from backEnd.app.utils.upload import upload_router
from backEnd.app.routers.routeGen_router import routeGen_router
from backEnd.app.routers.planGen_router import planGen_router

app = FastAPI()
app.include_router(db_router)
app.include_router(login_router)
app.include_router(user_router)
app.include_router(upload_router)
app.include_router(routeGen_router)
app.include_router(planGen_router)
