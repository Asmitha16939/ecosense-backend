import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os  # ← KEEP THIS!

# Get database URL from environment variable or use SQLite as fallback
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ecosense.db")

# If using MySQL, it will fail without proper credentials - fallback to SQLite
if DATABASE_URL.startswith("mysql"):
    try:
        engine = create_engine(DATABASE_URL)
    except:
        # Fallback to SQLite
        engine = create_engine("sqlite:///./ecosense.db")
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
