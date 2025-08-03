from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from services.user_service.app.config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
