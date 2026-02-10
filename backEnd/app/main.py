from fastapi import FastAPI
from backEnd.app.routers.account_router import account_router
from backEnd.app.routers.logs_router import frontend_logs_router
from backEnd.app.routers.user_router import user_router
from backEnd.app.utils.upload import upload_router
from backEnd.app.routers.routeGen_router import route_gen_router
from backEnd.app.routers.planGen_router import planGen_router

app = FastAPI()
app.include_router(account_router)
app.include_router(user_router)
app.include_router(upload_router)
app.include_router( route_gen_router )
app.include_router(planGen_router)
app.include_router(frontend_logs_router, prefix="/logs")
