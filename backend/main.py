# backend/main.py

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List
import os
import requests

from database import SessionLocal
from models import (
    User,
    Diet,
    Allergen,
    FoodPreference,
    UserDiet,
    UserAllergen,
    UserFoodPreference,
)

# ---- LLM / Ollama ayarları ----
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")

app = FastAPI()

# ---- CORS ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- DB Dependency ----
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------------
# Pydantic Schemas
# -------------------------

class ProfileCreate(BaseModel):
    email: str
    diets: List[int] = Field(default_factory=list)
    allergens: List[int] = Field(default_factory=list)
    food_preferences: List[int] = Field(default_factory=list)

class ChatRequest(BaseModel):
    user_id: int
    message: str

# -------------------------
# Helper Functions
# -------------------------

def build_prompt(db: Session, user_id: int, user_message: str) -> str:
    # ✅ PK: user_id
    user = db.query(User).filter(User.user_id == user_id).first()

    if not user:
        return "Kullanıcı profili yok.\n\nKullanıcı mesajı: " + user_message

    # ✅ DB kolon adlarına göre:
    # diet.diet_name, allergen.allergen_name, foodpreference.preference_name
    diets = [ud.diet.diet_name for ud in user.diets if ud.diet and ud.diet.diet_name]
    allergens = [ua.allergen.allergen_name for ua in user.allergens if ua.allergen and ua.allergen.allergen_name]
    foods = [uf.foodpreference.preference_name for uf in user.food_preferences if uf.foodpreference and uf.foodpreference.preference_name]

    profile_text = f"""
Kullanıcı Profili:

- Diyetler: {", ".join(diets) or "yok"}
- Alerjenler: {", ".join(allergens) or "yok"}
- Yemek tercihleri: {", ".join(foods) or "yok"}

Bu bilgilere göre kişiselleştirilmiş öneri yap.
"""

    return profile_text + "\nKullanıcı mesajı: " + user_message

# -------------------------
# Endpoints
# -------------------------

@app.post("/profile")
def create_profile(profile: ProfileCreate, db: Session = Depends(get_db)):
    user = User(email=profile.email)
    db.add(user)
    db.commit()
    db.refresh(user)

    # Join tablolar composite PK: aynı kayıt iki kez eklenirse hata verir.
    # O yüzden istersen set(...) yapıp duplicate'leri önleyebilirsin:
    for diet_id in set(profile.diets):
        db.add(UserDiet(user_id=user.user_id, diet_id=diet_id))

    for allergen_id in set(profile.allergens):
        db.add(UserAllergen(user_id=user.user_id, allergen_id=allergen_id))

    for pref_id in set(profile.food_preferences):
        db.add(UserFoodPreference(user_id=user.user_id, preference_id=pref_id))

    db.commit()

    return {"user_id": user.user_id}


@app.post("/chat")
def chat_with_llm(req: ChatRequest, db: Session = Depends(get_db)):
    prompt = build_prompt(db, req.user_id, req.message)

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }

    r = requests.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload)
    r.raise_for_status()

    data = r.json()
    answer = data.get("response", "")

    return {"answer": answer}
