from pydantic import BaseModel, constr
from typing import List, Optional, Union

# Pydantic Models (Data Validation & Serialization) (for API clients)

class UserBase(BaseModel):
    user: constr(min_length=1)

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    class Config:
        from_attributes = True 

class ItemBase(BaseModel):
    name: constr(min_length=1)
    description: Optional[Union[constr(min_length=1), None]] = None
    user_id: Optional[int] = None

class ItemCreate(ItemBase):
    pass

class ItemResponse(ItemBase):
    id: int
    class Config:
        from_attributes = True