from pydantic import BaseModel, ConfigDict

class UserRegister(BaseModel):
    username:str
    email:str
    password: str


class UserOut(BaseModel):
    pass