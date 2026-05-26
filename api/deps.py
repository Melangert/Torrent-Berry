from fastapi import Header, HTTPException
from auth import verify_token

async def require_auth(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authtorization header")
    token = authorization.removeprefix("Bearer ") 
    username = verify_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return username