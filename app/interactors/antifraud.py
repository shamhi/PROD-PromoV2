from httpx import AsyncClient

from app.core.exceptions import EntityAccessDeniedError
from app.schemas.common import Email, PromoId
from app.schemas.user import AntifraudResponse


class AntifraudInteractor:
    def __init__(self, http_client: AsyncClient):
        self.http_client = http_client

    async def __call__(self, user_email: Email, promo_id: PromoId) -> AntifraudResponse:
        headers = {"Content-Type": "application/json"}
        json = {"user_email": user_email, "promo_id": promo_id}

        for _ in range(2):
            try:
                response = await self.http_client.post(url="/api/validate", json=json, headers=headers)
                if response.status_code == 200:
                    response_data = response.json()
                    return AntifraudResponse(**response_data)
            except:  # noqa
                continue

        raise EntityAccessDeniedError
