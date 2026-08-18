from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings
import secrets

oauth2_scheme = HTTPBearer(auto_error=False)

async def verify_api_token(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    if not settings.MARKET_API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Server authentication is not configured.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    is_valid = secrets.compare_digest(credentials.credentials, settings.MARKET_API_TOKEN)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials
