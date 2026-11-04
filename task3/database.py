
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker, declarative_base

# PostgreSQL connection
DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username="postgres",
    password="Raji@0626",
    host="localhost",
    port=5432,
    database="retail_db"
)

# Connection pool
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    echo=True
)

# SessionLocal configuration
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False
)

# Base model
Base = declarative_base()
