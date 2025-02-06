from fastapi import APIRouter

from app.api.v2.endpoints import ping, user, auth, business

api_router = APIRouter()

api_router.include_router(ping.router, prefix="")
api_router.include_router(auth.router, prefix="")
api_router.include_router(user.router, prefix="/user")
api_router.include_router(business.router, prefix="/business")
