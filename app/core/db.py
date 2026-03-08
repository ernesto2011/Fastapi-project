import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from sqlalchemy.exc import OperationalError

import time

DATABASE_URL = os.getenv("DATABASE_URL","sqlite:///./blog.db")
print("conectado a:", DATABASE_URL)

engine_kwargs ={}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] ={"check_same_thread": False}
engine = create_engine(DATABASE_URL, echo=True, future=True, **engine_kwargs)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)


class Base(DeclarativeBase):
    pass

def get_db():
    db= SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
def wait_for_db(engine, retries=3, delay=2):
    for i in range(retries):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("✅ DB lista")
            return
        except OperationalError:
            print(f"⏳ DB no disponible... intento {i+1}")
            time.sleep(delay)
    raise RuntimeError("Database no disponible")