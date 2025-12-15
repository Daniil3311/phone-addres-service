from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from redis.asyncio import Redis

from app.schemas import (
    AddressUpdate,
    HealthResponse,
    MessageResponse,
    PhoneAddressCreate,
    PhoneAddressResponse,
)
from app.services import PhoneService
from app.storage.redis_repo import RedisRepository

router = APIRouter(prefix="/phones", tags=["phones"])


def get_redis(request: Request) -> Redis:
    client: Redis | None = getattr(request.app.state, "redis", None)
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Redis client is not initialized",
        )
    return client


async def get_repository(redis: Redis = Depends(get_redis)) -> RedisRepository:
    return RedisRepository(redis)


async def get_phone_service(
    repository: RedisRepository = Depends(get_repository),
) -> PhoneService:
    return PhoneService(repository)


@router.get("/{phone}", response_model=PhoneAddressResponse)
async def get_address(
    phone: str, service: PhoneService = Depends(get_phone_service)
) -> PhoneAddressResponse:
    return await service.get_phone(phone)


@router.post(
    "", status_code=status.HTTP_201_CREATED, response_model=MessageResponse
)
async def create_phone(
    data: PhoneAddressCreate, service: PhoneService = Depends(get_phone_service)
) -> MessageResponse:
    result = await service.create_phone(data)
    return MessageResponse(**result)


@router.put("/{phone}", response_model=MessageResponse)
async def update_address(
    phone: str, data: AddressUpdate, service: PhoneService = Depends(get_phone_service)
) -> MessageResponse:
    result = await service.update_address(phone, data)
    return MessageResponse(**result)


@router.delete(
    "/{phone}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def delete_phone(
    phone: str, service: PhoneService = Depends(get_phone_service)
) -> Response:
    await service.delete_phone(phone)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


health_router = APIRouter(tags=["health"])


@health_router.get("/health", response_model=HealthResponse)
async def health(redis: Redis = Depends(get_redis)) -> HealthResponse:
    repo = RedisRepository(redis)
    return HealthResponse(redis=await repo.ping())

