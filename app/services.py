from fastapi import HTTPException, status

from app.schemas import AddressUpdate, PhoneAddressCreate, PhoneAddressResponse
from app.storage.redis_repo import RedisRepository


class PhoneService:
    def __init__(self, repository: RedisRepository) -> None:
        self._repository = repository

    async def get_phone(self, phone: str) -> PhoneAddressResponse:
        address = await self._safe_call(self._repository.get(phone))
        if address is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Phone not found"
            )
        return PhoneAddressResponse(phone=phone, address=address)

    async def create_phone(self, data: PhoneAddressCreate) -> dict:
        created = await self._safe_call(
            self._repository.create(data.phone, data.address)
        )
        if not created:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Phone already exists"
            )
        return {"message": "Created successfully"}

    async def update_address(self, phone: str, data: AddressUpdate) -> dict:
        updated = await self._safe_call(
            self._repository.update(phone, data.address)
        )
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Phone not found"
            )
        return {"message": "Updated successfully"}

    async def delete_phone(self, phone: str) -> None:
        deleted = await self._safe_call(self._repository.delete(phone))
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Phone not found"
            )

    async def _safe_call(self, coro):
        try:
            return await coro
        except (ConnectionError, TimeoutError, OSError):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Redis is unavailable",
            )

