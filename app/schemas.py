from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

# Pydantic Models (Data Validation & Serialization) (for API clients)

class UserBase(BaseModel):
    login: str = Field(..., min_length=1, max_length=100)
    email: EmailStr = Field(...)
    password: str = Field(..., min_length=8, max_length=100)
    name: str | None = Field(default=None,  min_length=1)
    image_link: str | None = Field(default=None,  min_length=1) 
    # image_id: int | None

class UserCreate(UserBase):
    pass

class UserResponse(BaseModel):
    id: int
    login: str = Field(..., min_length=1, max_length=100)
    email: EmailStr = Field(...)
    name: str | None # = Field(default=None,  min_length=1)
    image_link: str | None # = Field(default=None,  min_length=1) 
    # image_id: int | None
    created_at: datetime
    updated_at: datetime

class UserResponsePublic(BaseModel):
    id: int
    login: str = Field(..., min_length=1, max_length=100)
    name: str | None = Field(default=None,  min_length=1)
    image_link: str | None = Field(default=None,  min_length=1) 
    # image_id: int | None

class UserEmailPassword(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(..., min_length=8, max_length=100)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: int 


class OutfitBase(BaseModel):
    name: str | None = Field(default=None,  min_length=1)
    description: str | None = Field(default=None,  min_length=1)
    image_link: str | None = Field(default=None,  min_length=1)
    # image_id: int | None
    user_id: int

class OutfitCreate(BaseModel):
    name: str | None = Field(default=None,  min_length=1)
    description: str | None = Field(default=None,  min_length=1)
    image_link: str | None = Field(default=None,  min_length=1)
    # image_id: int | None

class OutfitResponse(OutfitBase):
    id: int
    created_at: datetime
    updated_at: datetime
    # class Config:
    #     from_attributes = True


class GarmentBase(BaseModel):
    name: str | None = Field(default=None,  min_length=1)
    description: str | None = Field(default=None,  min_length=1)
    image_link: str | None = Field(default=None,  min_length=1)
    # image_id: int | None
    user_id: int
    last_worn: datetime | None = Field(default=None)
    gender_id: int | None = Field(default=None)
    category_master_id: int | None = Field(default=None)
    category_sub_id: int | None = Field(default=None)
    garment_type_id: int | None = Field(default=None)
    color_id: int | None = Field(default=None)
    season_id: int | None = Field(default=None)
    usage_id: int | None = Field(default=None)
    hex: str | None = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")

class GarmentCreate(BaseModel):
    name: str | None = Field(default=None,  min_length=1)
    description: str | None = Field(default=None,  min_length=1)
    image_link: str | None = Field(default=None,  min_length=1)
    # image_id: int | None
    last_worn: datetime | None = Field(default=None)
    gender_id: int | None = Field(default=None)
    category_master_id: int | None = Field(default=None)
    category_sub_id: int | None = Field(default=None)
    garment_type_id: int | None = Field(default=None)
    color_id: int | None = Field(default=None)
    season_id: int | None = Field(default=None)
    usage_id: int | None = Field(default=None)
    hex: str | None = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")

class GarmentClassify(BaseModel):
    gender_id: int | None = Field(default=None)
    category_master_id: int | None = Field(default=None)
    category_sub_id: int | None = Field(default=None)
    garment_type_id: int | None = Field(default=None)
    color_id: int | None = Field(default=None)
    season_id: int | None = Field(default=None)
    usage_id: int | None = Field(default=None)

class GarmentResponse(GarmentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    # class Config:
    #     from_attributes = True

class OutfitGarmentsUpdate(BaseModel):
    garment_ids: list[int]


class ImageInfoCreate(BaseModel):
    filename_store: str | None = Field(default=None,  min_length=1)
    filename_original: str | None = Field(default=None,  min_length=1)

class ImageInfoBase(BaseModel):
    filename_store: str | None = Field(default=None,  min_length=1)
    filename_original: str | None = Field(default=None,  min_length=1)
    user_id: int

class ImageInfoResponse(ImageInfoBase):
    id: int
    created_at: datetime
    updated_at: datetime

class GenderResponse(BaseModel):
    id: int
    name: str | None = Field(default=None,  min_length=1)
    description: str | None = Field(default=None,  min_length=1)
    created_at: datetime
    updated_at: datetime

class CategoryMasterResponse(BaseModel):
    id: int
    name: str | None = Field(default=None,  min_length=1)
    description: str | None = Field(default=None,  min_length=1)
    created_at: datetime
    updated_at: datetime

class CategorySubResponse(BaseModel):
    id: int
    name: str | None = Field(default=None,  min_length=1)
    description: str | None = Field(default=None,  min_length=1)
    created_at: datetime
    updated_at: datetime

class GarmentTypeResponse(BaseModel):
    id: int
    name: str | None = Field(default=None,  min_length=1)
    description: str | None = Field(default=None,  min_length=1)
    created_at: datetime
    updated_at: datetime

class ColorResponse(BaseModel):
    id: int
    name: str | None = Field(default=None,  min_length=1)
    description: str | None = Field(default=None,  min_length=1)
    hex: str | None = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")
    created_at: datetime
    updated_at: datetime

class SeasonResponse(BaseModel):
    id: int
    name: str | None = Field(default=None,  min_length=1)
    description: str | None = Field(default=None,  min_length=1)
    created_at: datetime
    updated_at: datetime

class UsageResponse(BaseModel):
    id: int
    name: str | None = Field(default=None,  min_length=1)
    description: str | None = Field(default=None,  min_length=1)
    created_at: datetime
    updated_at: datetime

class OutfitTemplateResponse(BaseModel):
    id: int
    name: str | None = Field(default=None,  min_length=1)
    description: str | None = Field(default=None,  min_length=1)
    created_at: datetime
    updated_at: datetime
    
class OutfitTemplateParameterResponse(BaseModel):
    outfit_template_id: int
    category_sub_id: int
    created_at: datetime

class CreateRandomOutfitParams(BaseModel):
    category_sub_ids: list[int]
    gender_ids: list[int] | None = Field(default=None)
