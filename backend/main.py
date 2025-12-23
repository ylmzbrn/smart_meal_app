# backend/main.py

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import List, Any, Optional
import os
import requests
import bcrypt

from database import get_db


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

app = FastAPI(
    title="Meal Selector API",
    description="Kişiselleştirilmiş yemek önerisi API'si",
    version="1.0.0"
)


# ---- CORS ----
FRONTEND_ORIGINS = os.getenv(
    "FRONTEND_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000"
)

origins = [origin.strip() for origin in FRONTEND_ORIGINS.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Pydantic Schemas
# -------------------------

class ProfileCreate(BaseModel):
    """
    ✅ Frontend email göndermiyor.
    ✅ user_id opsiyonel - gönderilmezse guest user kullanılır.
    ✅ diets/allergens/food_preferences artık ID değil İSİM listesi olacak.
       (frontend string gönderse bile kabul edip listeye çeviriyoruz)
    """
    user_id: Optional[int] = None  # Opsiyonel - yoksa guest user kullanılır
    diets: List[str] = Field(default_factory=list)
    allergens: List[str] = Field(default_factory=list)
    food_preferences: List[str] = Field(default_factory=list)

    @field_validator("diets", "allergens", "food_preferences", mode="before")
    @classmethod
    def normalize_list(cls, v: Any):
        """
        Kabul edilen inputlar:
        - ["vegan", "keto"]  ✅
        - "vegan"           ✅ -> ["vegan"]
        - "vegan, keto"     ✅ -> ["vegan", "keto"]
        """
        if v is None:
            return []
        if isinstance(v, list):
            return [str(x).strip() for x in v if str(x).strip()]
        if isinstance(v, str):
            return [x.strip() for x in v.split(",") if x.strip()]
        return v


class ChatRequest(BaseModel):
    user_id: int
    message: str


class RegisterRequest(BaseModel):
    """Kullanıcı kayıt şeması"""
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    """Kullanıcı giriş şeması"""
    email: str
    password: str


# -------------------------
# Auth Helper Functions
# -------------------------

def hash_password(password: str) -> str:
    """Şifreyi bcrypt ile hashle"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """Şifreyi doğrula"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


# -------------------------
# Helper Functions
# -------------------------

def _get_or_create_guest_user(db: Session) -> User:
    """
    Auth/login yoksa: tek bir 'guest' user üstünden profil tutuyoruz.
    İstersen ileride auth ekleyince burayı current_user'a bağlarız.
    """
    user = db.query(User).filter(User.username == "guest").first()
    if user:
        return user

    user = User(username="guest")  # email zorunlu değil (db'de nullable)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _get_or_create_by_name(db: Session, model_cls, name_field: str, value: str):
    """
    Diet/Allergen/FoodPreference tablosunda name yoksa oluşturur.
    model_cls: Diet | Allergen | FoodPreference
    name_field: DB'deki kolon adı (ör: 'diet_name' ya da 'name')
    """
    col = getattr(model_cls, name_field)
    obj = db.query(model_cls).filter(col == value).first()
    if obj:
        return obj

    obj = model_cls(**{name_field: value})
    db.add(obj)
    db.flush()  # id gelsin (commit öncesi)
    return obj


def _get_model_fields() -> dict:
    """
    models.py tarafında kolon isimleri farklı olabilir.
    Sen build_prompt içinde şu alanları kullanmışsın:
      Diet: diet_name
      Allergen: allergen_name
      FoodPreference: preference_name

    Eğer senin modellerin 'name' kullanıyorsa burayı değiştirmen yeter.
    """
    return {
        "diet_name": "diet_name",
        "allergen_name": "allergen_name",
        "preference_name": "preference_name",
        "diet_id": "diet_id",
        "allergen_id": "allergen_id",
        "preference_id": "preference_id",
    }


def build_prompt(db: Session, user_id: int, user_message: str) -> str:
    user = db.query(User).filter(User.user_id == user_id).first()

    if not user:
        return "Kullanıcı profili yok.\n\nKullanıcı mesajı: " + user_message

    f = _get_model_fields()

    # ✅ build_prompt senin mevcut ORM ilişkilerine göre bırakıldı.
    # (User -> UserDiet -> Diet gibi)
    diets = [
        getattr(ud.diet, f["diet_name"])
        for ud in getattr(user, "diets", [])
        if ud.diet and getattr(ud.diet, f["diet_name"], None)
    ]
    allergens = [
        getattr(ua.allergen, f["allergen_name"])
        for ua in getattr(user, "allergens", [])
        if ua.allergen and getattr(ua.allergen, f["allergen_name"], None)
    ]
    foods = [
        getattr(uf.foodpreference, f["preference_name"])
        for uf in getattr(user, "food_preferences", [])
        if uf.foodpreference and getattr(uf.foodpreference, f["preference_name"], None)
    ]

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

@app.post("/register")
def register_user(req: RegisterRequest, db: Session = Depends(get_db)):
    """
    Yeni kullanıcı kaydı
    - Email unique olmalı
    - Şifre bcrypt ile hashlenir
    """
    # Email zaten kayıtlı mı kontrol et
    existing_user = db.query(User).filter(User.email == req.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Bu e-posta adresi zaten kayıtlı."
        )
    
    # Yeni kullanıcı oluştur
    hashed_pw = hash_password(req.password)
    new_user = User(
        username=req.name,
        email=req.email,
        password_hash=hashed_pw
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "ok": True,
        "message": "Kayıt başarılı!",
        "user_id": new_user.user_id
    }


@app.post("/login")
def login_user(req: LoginRequest, db: Session = Depends(get_db)):
    """
    Kullanıcı girişi
    - Email ve şifre doğrulaması
    - Başarılı girişte user_id döner
    """
    # Kullanıcıyı bul
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        raise HTTPException(
            status_code=401,
            detail="E-posta veya şifre hatalı."
        )
    
    # Şifre kontrolü
    if not user.password_hash or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="E-posta veya şifre hatalı."
        )
    
    return {
        "ok": True,
        "message": "Giriş başarılı!",
        "user_id": user.user_id,
        "username": user.username,
        "token": f"user_{user.user_id}"  # Basit token (gerçek projede JWT kullan)
    }


@app.post("/profile")
def create_profile(profile: ProfileCreate, db: Session = Depends(get_db)):
    """
    ✅ Email beklemez.
    ✅ user_id opsiyonel - gönderilmezse guest user kullanılır.
    ✅ Frontend string veya list gönderebilir.
    ✅ DB'ye join tablolarıyla yazar.

    Davranış:
    - user_id varsa onu kullan, yoksa guest user'ı bul/oluştur
    - önce eski linkleri sil
    - sonra yeni diet/allergen/preference isimlerini (yoksa oluşturup) ilişkilendir
    """
    # user_id gönderilmişse onu kullan, yoksa guest user
    if profile.user_id:
        user = db.query(User).filter(User.user_id == profile.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
    else:
        user = _get_or_create_guest_user(db)

    f = _get_model_fields()

    # Eski ilişkileri temizle (update gibi davranır)
    db.query(UserDiet).filter(UserDiet.user_id == user.user_id).delete()
    db.query(UserAllergen).filter(UserAllergen.user_id == user.user_id).delete()
    db.query(UserFoodPreference).filter(UserFoodPreference.user_id == user.user_id).delete()
    db.flush()

    # Diets
    for name in set(profile.diets):
        name = name.strip()
        if not name:
            continue
        diet = _get_or_create_by_name(db, Diet, f["diet_name"], name)
        diet_id = getattr(diet, f["diet_id"])
        db.add(UserDiet(user_id=user.user_id, diet_id=diet_id))

    # Allergens
    for name in set(profile.allergens):
        name = name.strip()
        if not name:
            continue
        allergen = _get_or_create_by_name(db, Allergen, f["allergen_name"], name)
        allergen_id = getattr(allergen, f["allergen_id"])
        db.add(UserAllergen(user_id=user.user_id, allergen_id=allergen_id))

    # Food Preferences
    for name in set(profile.food_preferences):
        name = name.strip()
        if not name:
            continue
        pref = _get_or_create_by_name(db, FoodPreference, f["preference_name"], name)
        pref_id = getattr(pref, f["preference_id"])
        db.add(UserFoodPreference(user_id=user.user_id, preference_id=pref_id))

    db.commit()
    db.refresh(user)

    return {"ok": True, "user_id": user.user_id}


@app.post("/chat")
def chat_with_llm(req: ChatRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == req.user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found. Önce /profile kaydetmelisin."
        )

    prompt = build_prompt(db, req.user_id, req.message)

    try:
        r = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
            },
            timeout=120,
        )
        r.raise_for_status()
        data = r.json()
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="LLM'e bağlanılamadı. Ollama çalışmıyor olabilir."
        )
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=504,
            detail="LLM isteği zaman aşımına uğradı."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"LLM hatası: {str(e)}"
        )

    answer = (data.get("response") or "").strip()
    return {"answer": answer}
