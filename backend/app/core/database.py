from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.app.core.config import settings

# Optional: keep your manual test if you want
import pymysql
conn = pymysql.connect(host='localhost', port=3307, user='billing_user', password='@2000B1r1k1d1', db='billing_db')
print("Connected successfully")
conn.close()

print("DEBUG DATABASE_URL =", settings.DATABASE_URL)


engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,      # helps with stale connections
    echo=False               # set True temporarily to see SQL
)  # ← No connect_args


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()






