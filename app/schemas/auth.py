from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):

    nama: str

    email: EmailStr

    password: str


class LoginRequest(BaseModel):

    email: EmailStr

    password: str