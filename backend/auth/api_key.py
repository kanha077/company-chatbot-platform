from fastapi.security import APIKeyHeader
from fastapi import Security, HTTPException
from config import API_SECRET_KEY

API_KEY_HEADER = APIKeyHeader(name="X-API-Key")

def verify_api_key(api_key: str = Security(API_KEY_HEADER)):
    if api_key != API_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")
    return api_key
