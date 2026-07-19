from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_respond
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

class RateLimitManager:
    def __init__(self):
        self.limiter = Limiter(key_func=get_remote_address)

    def setup(self, app: FastAPI) -> None:
        """Hooks the limiter into the FastAPI application state and error handlers."""
        app.state.limiter = self.limiter
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_respond)


rate_limit_manager = RateLimitManager()
limiter = rate_limit_manager.limiter