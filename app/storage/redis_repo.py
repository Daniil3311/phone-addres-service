from typing import Optional

from redis.asyncio import Redis


class RedisRepository:
    def __init__(self, client: Redis) -> None:
        self._client = client

    async def get(self, phone: str) -> Optional[str]:
        return await self._client.get(phone)

    async def create(self, phone: str, address: str) -> bool:
        # Create only if not exists (NX)
        return await self._client.set(phone, address, nx=True) is True

    async def update(self, phone: str, address: str) -> bool:
        # Update only if exists (XX)
        return await self._client.set(phone, address, xx=True) is True

    async def delete(self, phone: str) -> bool:
        deleted = await self._client.delete(phone)
        return deleted > 0

    async def ping(self) -> bool:
        try:
            return await self._client.ping() is True
        except Exception:
            return False

