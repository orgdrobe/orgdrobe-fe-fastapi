from pydantic import BaseModel, EmailStr, ConfigDict, Field

class UserRegister(BaseModel):
    username:str
    email:str
    password: str

class UserLogin(BaseModel):
    email: str 
    password: str

class ForgotPassword(BaseModel):
    email: EmailStr

class ResetPassword(BaseModel):
    token: str
    password: str

class ResendVerificationCode(BaseModel):
    email: EmailStr

class AccountVerification(BaseModel):
    email: EmailStr
    code: str

class UserRegisterOut(BaseModel):
    id: int
    email: EmailStr
    is_email_verified: bool

    model_config = ConfigDict(from_attributes=True)

class UserLoginOut(BaseModel):
    access_token: str = ""
    expires_in: int = -1
    token_type: str = "bearer"

    model_config = ConfigDict(validate_default=True)


