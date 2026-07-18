from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from kyc.config.settings import settings

DATABASE_URL = settings.database.url

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True # Automatically verifies connection health
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# FastAPI Dependency injection to open/close DB sessions safely
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
