import jwt  # PyJWT for token verification
from typing import Optional
from fastapi import Header, HTTPException
import os

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"

# -------------------------------
# JWT Token Validation
# -------------------------------
def verify_token(authorization: Optional[str] = Header(None)):
    """Verify JWT token from Authorization header (provided by another server)."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    token = authorization.split(" ")[1]  # Extract token after "Bearer"
    
    try:
        # Decode token using the provided JWT secret key
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload  # Return decoded token payload (e.g., user info)
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")