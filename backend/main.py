"""
main.py - FastAPI Backend
smart_eats veritabanıyla çalışan API endpoint'leri.

Endpoints:
- POST /register - Kullanıcı kaydı
- POST /login - Kullanıcı girişi
- POST /profile - Kullanıcı profil tercihleri (diyet, alerji, kısıtlı besinler)
- POST /llm/recommend - LLM ile yemek önerisi
"""

import os
import requests
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List

from database import get_db, init_db
from models import User, Diet, Allergen, FoodPreference, UserDiet, UserAllergen, UserFoodPreference


# ============================================
# LLM / Ollama Ayarları
# ============================================
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma:4b")


# ============================================
# FastAPI Uygulaması
# ============================================
app = FastAPI(
    title="Meal Selector API",
    description="Kişiselleştirilmiş yemek önerisi API'si",
    version="1.0.0"
)


# CORS Ayarları (React frontend için)
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# Pydantic Modelleri (Request/Response)
# ============================================

class RegisterRequest(BaseModel):
    """Kullanıcı kayıt isteği"""
    name: str
    email: str
    password: str


class RegisterResponse(BaseModel):
    """Kullanıcı kayıt yanıtı"""
    user_id: int
    username: str
    email: str
    message: str


class LoginRequest(BaseModel):
    """Kullanıcı giriş isteği"""
    email: str
    password: str


class LoginResponse(BaseModel):
    """Kullanıcı giriş yanıtı"""
    user_id: int
    username: str
    email: str
    message: str


class ProfileRequest(BaseModel):
    """Kullanıcı profil tercihleri isteği"""
    user_id: int
    diet_preferences: Optional[str] = ""  # Virgülle ayrılmış: "vegan, glutensiz"
    allergies: Optional[str] = ""          # Virgülle ayrılmış: "fıstık, süt"
    restricted_foods: Optional[str] = ""   # Virgülle ayrılmış: "domuz, alkol"


class ProfileResponse(BaseModel):
    """Kullanıcı profil yanıtı"""
    user_id: int
    diets: List[str]
    allergens: List[str]
    restricted_foods: List[str]
    message: str


class ChatRequest(BaseModel):
    """LLM sohbet isteği"""
    user_id: int
    message: str = "Bugün ne yesem?"


# ============================================
# Yardımcı Fonksiyonlar
# ============================================

def parse_comma_separated(text: str) -> List[str]:
    """
    Virgülle ayrılmış string'i listeye çevirir.
    Boşlukları temizler, boş elemanları atar.
    """
    if not text:
        return []
    return [item.strip() for item in text.split(",") if item.strip()]


def get_or_create_diet(db: Session, name: str) -> Diet:
    """Diyet varsa getir, yoksa oluştur."""
    diet = db.query(Diet).filter(Diet.diet_name == name).first()
    if not diet:
        diet = Diet(diet_name=name)
        db.add(diet)
        db.commit()
        db.refresh(diet)
    return diet


def get_or_create_allergen(db: Session, name: str) -> Allergen:
    """Alerjen varsa getir, yoksa oluştur."""
    allergen = db.query(Allergen).filter(Allergen.allergen_name == name).first()
    if not allergen:
        allergen = Allergen(allergen_name=name)
        db.add(allergen)
        db.commit()
        db.refresh(allergen)
    return allergen


def get_or_create_food_preference(db: Session, name: str) -> FoodPreference:
    """Yiyecek tercihi varsa getir, yoksa oluştur."""
    food_pref = db.query(FoodPreference).filter(FoodPreference.preference_name == name).first()
    if not food_pref:
        food_pref = FoodPreference(preference_name=name)
        db.add(food_pref)
        db.commit()
        db.refresh(food_pref)
    return food_pref


def get_user_diets(db: Session, user_id: int) -> List[str]:
    """Kullanıcının diyetlerini getir."""
    user_diets = db.query(UserDiet).filter(UserDiet.user_id == user_id).all()
    diets = []
    for ud in user_diets:
        diet = db.query(Diet).filter(Diet.diet_id == ud.diet_id).first()
        if diet:
            diets.append(diet.diet_name)
    return diets


def get_user_allergens(db: Session, user_id: int) -> List[str]:
    """Kullanıcının alerjenlerini getir."""
    user_allergens = db.query(UserAllergen).filter(UserAllergen.user_id == user_id).all()
    allergens = []
    for ua in user_allergens:
        allergen = db.query(Allergen).filter(Allergen.allergen_id == ua.allergen_id).first()
        if allergen:
            allergens.append(allergen.allergen_name)
    return allergens


def get_user_restricted_foods(db: Session, user_id: int) -> List[str]:
    """Kullanıcının kısıtlı besinlerini getir."""
    user_foods = db.query(UserFoodPreference).filter(UserFoodPreference.user_id == user_id).all()
    foods = []
    for uf in user_foods:
        food = db.query(FoodPreference).filter(FoodPreference.preference_id == uf.preference_id).first()
        if food:
            foods.append(food.preference_name)
    return foods


# ============================================
# Uygulama Başlangıcı
# ============================================

@app.on_event("startup")
def on_startup():
    """Uygulama başladığında çalışır."""
    init_db()


# ============================================
# API Endpoints
# ============================================

@app.get("/")
def home():
    """Ana sayfa - API durumu."""
    return {"message": "Meal Selector API çalışıyor!", "version": "1.0.0"}


# -----------------------------
# REGISTER - Kullanıcı Kaydı
# -----------------------------
@app.post("/register", response_model=RegisterResponse)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Yeni kullanıcı kaydı oluşturur.
    
    - "User" tablosuna kayıt yapar
    - Email benzersiz olmalı
    - password_hash alanına şimdilik düz metin kaydedilir
    """
    # Email kontrolü
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Bu e-posta adresi zaten kayıtlı."
        )
    
    # Yeni kullanıcı oluştur
    new_user = User(
        username=request.name,
        email=request.email,
        password_hash=request.password  # TODO: Gerçek uygulamada hash'lenmeli
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return RegisterResponse(
        user_id=new_user.user_id,
        username=new_user.username or "",
        email=new_user.email,
        message="Kayıt başarılı!"
    )


# -----------------------------
# LOGIN - Kullanıcı Girişi
# -----------------------------
@app.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Kullanıcı girişi yapar.
    
    - Email ile kullanıcıyı bulur
    - password_hash ile karşılaştırır
    - Başarılı ise user_id döndürür
    """
    # Kullanıcıyı bul
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Bu e-posta adresiyle kayıtlı kullanıcı bulunamadı."
        )
    
    # Şifre kontrolü (şimdilik düz metin karşılaştırma)
    if user.password_hash != request.password:
        raise HTTPException(
            status_code=401,
            detail="Şifre hatalı."
        )
    
    return LoginResponse(
        user_id=user.user_id,
        username=user.username or "",
        email=user.email,
        message="Giriş başarılı!"
    )


# -----------------------------
# PROFILE - Kullanıcı Profili
# -----------------------------
@app.post("/profile", response_model=ProfileResponse)
def update_profile(request: ProfileRequest, db: Session = Depends(get_db)):
    """
    Kullanıcının profil tercihlerini günceller.
    
    İşleyiş:
    - Diyetler → diet + userdiet tablolarına
    - Alerjenler → allergen + userallergen tablolarına
    - Kısıtlı besinler → foodpreference + userfoodpreference tablolarına
    
    Eğer isim DB'de yoksa oluşturur, varsa mevcut olanı kullanır.
    Aynı ilişki tekrar eklenirse hata vermez.
    """
    # Kullanıcı var mı kontrol et
    user = db.query(User).filter(User.user_id == request.user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"Kullanıcı bulunamadı (user_id: {request.user_id})"
        )
    
    # Mevcut ilişkileri temizle (yeniden oluşturmak için)
    db.query(UserDiet).filter(UserDiet.user_id == request.user_id).delete()
    db.query(UserAllergen).filter(UserAllergen.user_id == request.user_id).delete()
    db.query(UserFoodPreference).filter(UserFoodPreference.user_id == request.user_id).delete()
    db.commit()
    
    # Diyetleri ekle
    diet_names = parse_comma_separated(request.diet_preferences)
    for diet_name in diet_names:
        diet = get_or_create_diet(db, diet_name)
        user_diet = UserDiet(user_id=request.user_id, diet_id=diet.diet_id)
        db.add(user_diet)
    
    # Alerjenleri ekle
    allergen_names = parse_comma_separated(request.allergies)
    for allergen_name in allergen_names:
        allergen = get_or_create_allergen(db, allergen_name)
        user_allergen = UserAllergen(user_id=request.user_id, allergen_id=allergen.allergen_id)
        db.add(user_allergen)
    
    # Kısıtlı besinleri ekle
    food_names = parse_comma_separated(request.restricted_foods)
    for food_name in food_names:
        food_pref = get_or_create_food_preference(db, food_name)
        user_food = UserFoodPreference(user_id=request.user_id, preference_id=food_pref.preference_id)
        db.add(user_food)
    
    db.commit()
    
    return ProfileResponse(
        user_id=request.user_id,
        diets=diet_names,
        allergens=allergen_names,
        restricted_foods=food_names,
        message="Profil başarıyla güncellendi!"
    )


# -----------------------------
# GET PROFILE - Profil Bilgilerini Getir
# -----------------------------
@app.get("/profile/{user_id}")
def get_profile(user_id: int, db: Session = Depends(get_db)):
    """
    Kullanıcının mevcut profil bilgilerini getirir.
    """
    # Kullanıcı var mı kontrol et
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"Kullanıcı bulunamadı (user_id: {user_id})"
        )
    
    diets = get_user_diets(db, user_id)
    allergens = get_user_allergens(db, user_id)
    restricted_foods = get_user_restricted_foods(db, user_id)
    
    return {
        "user_id": user_id,
        "username": user.username,
        "email": user.email,
        "diets": diets,
        "allergens": allergens,
        "restricted_foods": restricted_foods
    }


# -----------------------------
# LLM RECOMMEND - Yemek Önerisi
# -----------------------------
@app.post("/llm/recommend")
def get_meal_recommendation(chat: ChatRequest, db: Session = Depends(get_db)):
    """
    Kullanıcının profilini DB'den alır,
    prompt hazırlar,
    Ollama'daki LLM'e gönderir,
    cevabı geri döndürür.
    
    ⚠️ user_profiles tablosu YOK - Normalize tablolar kullanılıyor:
    - userdiet
    - userallergen
    - userfoodpreference
    """
    # Kullanıcı var mı kontrol et
    user = db.query(User).filter(User.user_id == chat.user_id).first()
    if not user:
        return {
            "error": "Kullanıcı bulunamadı. Önce kayıt olun.",
            "user_id": chat.user_id,
        }
    
    # Kullanıcının tercihlerini normalize tablolardan çek
    diets = get_user_diets(db, chat.user_id)
    allergens = get_user_allergens(db, chat.user_id)
    restricted_foods = get_user_restricted_foods(db, chat.user_id)
    
    # Profil bilgilerini string'e çevir
    diet_str = ", ".join(diets) if diets else "Belirtilmemiş"
    allergen_str = ", ".join(allergens) if allergens else "Yok"
    restricted_str = ", ".join(restricted_foods) if restricted_foods else "Yok"
    
    # LLM Prompt'u hazırla
    prompt = f"""
Sen bir yapay zeka yemek önerisi asistanısın.

Kullanıcının profili:
- Beslenme tercihleri: {diet_str}
- Alerjiler: {allergen_str}
- Kısıtlı besinler: {restricted_str}

Kullanıcı sana şu mesajı gönderiyor:
\"\"\"{chat.message}\"\"\"

Kurallar:
- Kullanıcıya alerjisi olan hiçbir şeyi önermeyeceksin.
- Kısıtlı besinleri içeren hiçbir yemek önermeyeceksin.
- Kullanıcının beslenme tercihiyle uyumlu öneriler ver.
- En az 3 öneri yap, maddeler halinde yaz.
- Açıklamaları kısa ve anlaşılır yap.
"""

    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
            },
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        return {
            "error": "LLM'e bağlantı sağlanamadı. Ollama çalışmıyor olabilir.",
            "ollama_url": OLLAMA_BASE_URL,
        }
    except Exception as e:
        return {
            "error": "LLM isteği sırasında hata oluştu.",
            "details": str(e),
        }

    data = response.json()
    llm_answer = data.get("response", "").strip()

    return {
        "profile_used": {
            "diets": diets,
            "allergens": allergens,
            "restricted_foods": restricted_foods,
        },
        "user_message": chat.message,
        "llm_answer": llm_answer,
    }
