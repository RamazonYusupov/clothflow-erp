from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus
import os
from dotenv import load_dotenv

load_dotenv()

# Build DATABASE_URL from individual parts so special characters in the
# password are always URL-encoded correctly — no matter what password is set.
def _build_url() -> str:
    # If a full DATABASE_URL is provided and it doesn't contain special chars,
    # use it directly. Otherwise build from parts.
    url = os.getenv("DATABASE_URL", "")
    if url:
        return url

    user     = os.getenv("POSTGRES_USER",     "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "password")
    host     = os.getenv("POSTGRES_HOST",     "db")
    port     = os.getenv("POSTGRES_PORT",     "5432")
    db       = os.getenv("POSTGRES_DB",       "retail_erp")

    # quote_plus encodes @, !, #, $ etc. so the URL parser never misreads them
    return f"postgresql://{quote_plus(user)}:{quote_plus(password)}@{host}:{port}/{db}"


DATABASE_URL = _build_url()

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
