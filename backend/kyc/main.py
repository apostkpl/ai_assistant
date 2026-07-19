import logging
import sys
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError
from sqlalchemy import text

from kyc.config.settings import settings
from kyc.core.database import engine
import kyc.models  # Ensure all models are imported for Alembic migrations
from kyc.routers.auth_router import router as auth_router
from kyc.routers.users_router import router as users_router
from kyc.routers.system_router import router as system_router

# Configure global basic logging for the application startup
""" CHANGE LEVELTO INFO IN PRODUCTION"""
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 1. Fail early if the database URL is not set in the environment variables
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles application startup and shutdown tasks natively inside the event loop.
    Guarantees the application blocks safely until dependencies are verified.
    """
    logger.info("Verifying database connectivity...")
    try:
        # Check if the connection pool can successfully check-in a query
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        logger.info("Database connectivity verified successfully.")
    except OperationalError as e:
        logger.critical(
            f"CRITICAL: Failed to connect to the database at launch!\n"
            f"Verify your Podman container status and environment configurations. Error: {str(e)}"
        )
        sys.exit(1)

    yield

    logger.info("Cleaning up DB connection pools...")
    engine.dispose()

# 2. Boot up the FastAPI Application
app = FastAPI(
    title="My App Authentication Service",
    description="KYC and security",
    version="1.0.0",
    lifespan=lifespan  # Use the lifespan context manager for early database connectivity checks
)

# 3. Apply CORS Middleware
logger.info(f"Configuring CORS for origins: {settings.cors.cors_origins}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers (including Authorization for our JWTs)
)

# 4. Register API Routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(system_router)

logger.info("Application successfully booted and ready for traffic.")
