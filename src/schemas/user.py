from pydantic import BaseModel, EmailStr, ConfigDict

class UserRegister(BaseModel):
    username:str
    email:str
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    is_email_verified: bool

    model_config = ConfigDict(from_attributes=True)