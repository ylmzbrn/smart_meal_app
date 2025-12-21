"""
database.py - PostgreSQL Veritabanı Bağlantısı
smart_eats veritabanına bağlantı ayarları.

⚠️ DİKKAT: Mevcut tablolar kullanılıyor, yeni tablo OLUŞTURULMUYOR.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# PostgreSQL bağlantı bilgileri
SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres:abc123@localhost:5432/smart_eats"

# Engine oluştur
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def init_db():
    """
    Veritabanı başlatma fonksiyonu.
    ⚠️ create_all() KALDIRILDI - Mevcut tablolar zaten var, yeni tablo oluşturulmayacak.
    """
    # Base.metadata.create_all(bind=engine)  # DEVRE DIŞI - Yeni tablo oluşturmuyoruz
    pass


def get_db():
    """
    Dependency injection için veritabanı session'ı döndürür.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
