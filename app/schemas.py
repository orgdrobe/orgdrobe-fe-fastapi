from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

# Pydantic Models (Data Validation & Serialization) (for API clients)

class UserBase(BaseModel):
    login: str = Field(..., min_length=1, max_length=100)
    email: EmailStr = Field(...)
    password: str = Field(..., min_length=8, max_length=100)
    name: str | None = Field(default=None,  min_length=1)
    picture: str | None = Field(default=None,  min_length=1) 

class UserCreate(UserBase):
    pass

class UserResponse(BaseModel):
    id: int
    login: str = Field(..., min_length=1, max_length=100)
    email: EmailStr = Field(...)
    name: str | None # = Field(default=None,  min_length=1)
    picture: str | None # = Field(default=None,  min_length=1) 
    created_at: datetime
    updated_at: datetime

class UserResponsePublic(BaseModel):
    id: int
    login: str = Field(..., min_length=1, max_length=100)
    name: str | None = Field(default=None,  min_length=1)
    picture: str | None = Field(default=None,  min_length=1) 

class UserEmailPassword(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(..., min_length=8, max_length=100)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: int 


class GarmentBase(BaseModel):
    name: str | None = Field(default=None,  min_length=1)
    description: str | None = Field(default=None,  min_length=1)
    user_id: int

class GarmentCreate(BaseModel):
    name: str | None = Field(default=None,  min_length=1)
    description: str | None = Field(default=None,  min_length=1)

class GarmentResponse(GarmentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    # class Config:
    #     from_attributes = True