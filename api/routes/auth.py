from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from auth import authenticate

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
def login(body: LoginRequest):
    token =  authenticate(body.username, body.password)
    if not token:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    return {"token":token}

