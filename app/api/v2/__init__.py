from fastapi import APIRouter

from app.api.v2.endpoints import auth, business, ping, user

root_router = APIRouter()

sub_routers = (
    ping.router,
    auth.router,
    business.router,
    user.router,
)

for router in sub_routers:
    root_router.include_router(router)
