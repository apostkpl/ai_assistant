import logging
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from kyc.config.settings import settings
from kyc.core.database import get_db
from kyc.models.user import User
from kyc.core.security import ALGORITHM

logger = logging.getLogger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
) -> User:
    """
    Intercepts the incoming request, extracts the Bearer token from the headers,
    decodes it, and fetches the full User object from the database.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.app.secret_key, algorithms=[ALGORITHM])
        email: str | None = payload.get("sub") # sub = email/username
        if email is None:
            raise credentials_exception
            
    except jwt.ExpiredSignatureError:
        logger.warning("Token validation failed: Token has expired.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Token has expired. Please log in again."
        )
    except jwt.PyJWTError:
        logger.warning("Token validation failed: Invalid token signature.")
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
        
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    A secondary dependency that ensures the user hasn't been banned or deactivated 
    since their token was issued.
    """
    if not current_user.is_active: # type: ignore
        logger.warning(f"Access denied for inactive user: {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Inactive user account"
        )
    return current_user