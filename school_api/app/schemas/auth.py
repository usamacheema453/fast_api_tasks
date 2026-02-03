from pydantic import BaseModel, EmailStr

class RegisterIn(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role_name: str

class Login(BaseModel):
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str
    token_type: str = "bearer"