import os
from sqlalchemy import Column, Integer, String, DateTime, JSON, text
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Resolve DATABASE_URL with auto‑fixes
raw_url = os.getenv("DATABASE_URL", os.getenv("POSTGRES_URL", "sqlite:///./app.db"))
if raw_url.startswith("postgresql+asyncpg://"):
    raw_url = raw_url.replace("postgresql+asyncpg://", "postgresql+psycopg://")
elif raw_url.startswith("postgres://"):
    raw_url = raw_url.replace("postgres://", "postgresql+psycopg://")

# Determine if we need SSL for PostgreSQL (non‑localhost & not SQLite)
connect_args = {}
if raw_url.startswith("postgresql+psycopg://") and "localhost" not in raw_url and "127.0.0.1" not in raw_url:
    connect_args = {"sslmode": "require"}

engine = create_engine(raw_url, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

Base = declarative_base()

class Bookmark(Base):
    __tablename__ = "qm_bookmarks"  # prefixed to avoid collisions
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    title = Column(String, nullable=True)
    tags = Column(JSON, nullable=False, server_default=text("'[]'"))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
