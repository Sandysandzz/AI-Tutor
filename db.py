# backend/db.py

from sqlalchemy.orm import sessionmaker
from backend.models import get_engine

# Create engine
engine = get_engine()

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
