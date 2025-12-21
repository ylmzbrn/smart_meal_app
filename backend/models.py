"""
models.py - PostgreSQL Veritabanı Modelleri
smart_eats veritabanındaki mevcut tablolarla eşleştirilmiş SQLAlchemy modelleri.

⚠️ DİKKAT: Bu modeller mevcut tabloları OKUYOR, yeni tablo OLUŞTURMUYOR.

Kolon İsimleri (DB'den alındı):
- User: user_id, username, email, password_hash
- diet: diet_id, diet_name
- allergen: allergen_id, allergen_name
- foodpreference: preference_id, preference_name
- userdiet: user_id, diet_id
- userallergen: user_id, allergen_id
- userfoodpreference: user_id, preference_id
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    """
    "User" tablosu (case-sensitive, çift tırnak gerekli)
    """
    __tablename__ = "User"
    
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=True)
    email = Column(String(150), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    
    # İlişkiler
    diets = relationship("UserDiet", back_populates="user")
    allergens = relationship("UserAllergen", back_populates="user")
    food_preferences = relationship("UserFoodPreference", back_populates="user")


class Diet(Base):
    """
    diet tablosu - Diyet türleri (vegan, glutensiz, vb.)
    """
    __tablename__ = "diet"
    
    diet_id = Column(Integer, primary_key=True, index=True)
    diet_name = Column(String(100), unique=True, nullable=False)
    
    # İlişki
    users = relationship("UserDiet", back_populates="diet")


class Allergen(Base):
    """
    allergen tablosu - Alerjen türleri (fıstık, süt, vb.)
    """
    __tablename__ = "allergen"
    
    allergen_id = Column(Integer, primary_key=True, index=True)
    allergen_name = Column(String(100), unique=True, nullable=False)
    
    # İlişki
    users = relationship("UserAllergen", back_populates="allergen")


class FoodPreference(Base):
    """
    foodpreference tablosu - Yiyecek tercihleri/kısıtlamaları
    """
    __tablename__ = "foodpreference"
    
    preference_id = Column(Integer, primary_key=True, index=True)
    preference_name = Column(String(100), unique=True, nullable=False)
    
    # İlişki
    users = relationship("UserFoodPreference", back_populates="food_preference")


class UserDiet(Base):
    """
    userdiet tablosu - Kullanıcı-Diyet ilişki tablosu (many-to-many)
    """
    __tablename__ = "userdiet"
    
    user_id = Column(Integer, ForeignKey("User.user_id"), primary_key=True)
    diet_id = Column(Integer, ForeignKey("diet.diet_id"), primary_key=True)
    
    # İlişkiler
    user = relationship("User", back_populates="diets")
    diet = relationship("Diet", back_populates="users")


class UserAllergen(Base):
    """
    userallergen tablosu - Kullanıcı-Alerjen ilişki tablosu (many-to-many)
    """
    __tablename__ = "userallergen"
    
    user_id = Column(Integer, ForeignKey("User.user_id"), primary_key=True)
    allergen_id = Column(Integer, ForeignKey("allergen.allergen_id"), primary_key=True)
    
    # İlişkiler
    user = relationship("User", back_populates="allergens")
    allergen = relationship("Allergen", back_populates="users")


class UserFoodPreference(Base):
    """
    userfoodpreference tablosu - Kullanıcı-YiyecekTercihi ilişki tablosu (many-to-many)
    """
    __tablename__ = "userfoodpreference"
    
    user_id = Column(Integer, ForeignKey("User.user_id"), primary_key=True)
    preference_id = Column(Integer, ForeignKey("foodpreference.preference_id"), primary_key=True)
    
    # İlişkiler
    user = relationship("User", back_populates="food_preferences")
    food_preference = relationship("FoodPreference", back_populates="users")
