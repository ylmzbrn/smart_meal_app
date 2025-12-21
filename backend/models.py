# backend/models.py

from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base


# --------------------
# USER
# --------------------
class User(Base):
    __tablename__ = "User"  # DB: public."User"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=True)
    email = Column(String(150), unique=True, index=True, nullable=True)
    password_hash = Column(Text, nullable=True)

    diets = relationship("UserDiet", back_populates="user", cascade="all, delete-orphan")
    allergens = relationship("UserAllergen", back_populates="user", cascade="all, delete-orphan")
    food_preferences = relationship("UserFoodPreference", back_populates="user", cascade="all, delete-orphan")


# --------------------
# DIET
# --------------------
class Diet(Base):
    __tablename__ = "diet"

    diet_id = Column(Integer, primary_key=True, index=True)
    diet_name = Column(String(100), nullable=True)




# --------------------
# ALLERGEN
# --------------------
class Allergen(Base):
    __tablename__ = "allergen"

    allergen_id = Column(Integer, primary_key=True, index=True)
    allergen_name = Column(String(100), nullable=True)



# --------------------
# FOOD PREFERENCE
# --------------------
class FoodPreference(Base):
    __tablename__ = "foodpreference"

    preference_id = Column(Integer, primary_key=True, index=True)
    preference_name = Column(String(100), nullable=True)




# --------------------
# USER ↔ DIET
# --------------------
class UserDiet(Base):
    __tablename__ = "userdiet"

    user_id = Column(Integer, ForeignKey('User.user_id'), primary_key=True)
    diet_id = Column(Integer, ForeignKey("diet.diet_id"), primary_key=True)

    user = relationship("User", back_populates="diets")
    diet = relationship("Diet")




# --------------------
# USER ↔ ALLERGEN
# --------------------
class UserAllergen(Base):
    __tablename__ = "userallergen"

    user_id = Column(Integer, ForeignKey('User.user_id'), primary_key=True)
    allergen_id = Column(Integer, ForeignKey("allergen.allergen_id"), primary_key=True)

    user = relationship("User", back_populates="allergens")
    allergen = relationship("Allergen")




# --------------------
# USER ↔ FOOD PREFERENCE
# --------------------
class UserFoodPreference(Base):
    __tablename__ = "userfoodpreference"

    user_id = Column(Integer, ForeignKey('User.user_id'), primary_key=True)
    preference_id = Column(Integer, ForeignKey("foodpreference.preference_id"), primary_key=True)

    user = relationship("User", back_populates="food_preferences")
    foodpreference = relationship("FoodPreference")



