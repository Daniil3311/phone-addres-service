import re
from pydantic import BaseModel, Field, field_validator

PHONE_REGEX = re.compile(r"^\+?\d{10,15}$")


class AddressBase(BaseModel):
    address: str = Field(min_length=1, max_length=200)

    @field_validator("address")
    @classmethod
    def strip_address(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Address must not be empty")
        return value


class PhoneAddressCreate(AddressBase):
    phone: str = Field(min_length=10, max_length=16)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        value = value.strip()
        if not PHONE_REGEX.match(value):
            raise ValueError("Phone must be digits (10-15) with optional leading +")
        return value


class AddressUpdate(AddressBase):
    pass


class PhoneAddressResponse(BaseModel):
    phone: str
    address: str


class MessageResponse(BaseModel):
    message: str


class HealthResponse(BaseModel):
    redis: bool
