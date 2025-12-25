# backend/main.py
from schemas import (
    RestaurantCreate,
    RestaurantOut,
    MenuItemCreate,
    MenuItemOut,
)
from ollama_client import ask_ollama
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
    MenuItem,
    Restaurant,
)



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

def get_full_menu(db: Session):
    results = (
        db.query(
            Restaurant.restaurant_id,
            Restaurant.restaurant_name,
            MenuItem.food_id,
            MenuItem.name.label("food_name"),
            MenuItem.price,
            MenuItem.allergy,
            MenuItem.description,
        )
        .join(MenuItem, MenuItem.restaurant_id == Restaurant.restaurant_id)
        .all()
    )

    menu = {}
    for r in results:
        if r.restaurant_id not in menu:
            menu[r.restaurant_id] = {
                "restaurant_name": r.restaurant_name,
                "foods": []
            }

        menu[r.restaurant_id]["foods"].append({
            "food_id": r.food_id,
            "name": r.food_name,
            "price": str(r.price) if r.price else None,
            "allergy": r.allergy,
            "description": r.description
        })

    return menu

def filter_menu_by_allergen(menu: dict, user_allergens: list[str]):
    safe_menu = {}

    for rid, data in menu.items():
        safe_foods = []

        for food in data["foods"]:
            if not food["allergy"]:
                safe_foods.append(food)
                continue

            food_allergy = food["allergy"].lower()
            if any(a in food_allergy for a in user_allergens):
                continue  # ❌ alerjenli → atla

            safe_foods.append(food)

        if safe_foods:
            safe_menu[rid] = {
                "restaurant_name": data["restaurant_name"],
                "foods": safe_foods
            }

    return safe_menu

def build_menu_text(menu: dict) -> str:
    """
    SADECE SAFE menu almalıdır
    """
    lines = []

    for data in menu.values():
        lines.append(f"Restoran: {data['restaurant_name']}")
        for f in data["foods"]:
            line = f"- {f['name']}"
            if f.get("description"):
                line += f" ({f['description']})"
            if f.get("price"):
                line += f" | Fiyat: {f['price']} TL"
            lines.append(line)
        lines.append("")  # boş satır

    return "\n".join(lines)






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


@app.post("/restaurants", response_model=RestaurantOut)
def create_restaurant(
    restaurant: RestaurantCreate,
    db: Session = Depends(get_db)
):
    db_restaurant = Restaurant(**restaurant.dict())
    db.add(db_restaurant)
    db.commit()
    db.refresh(db_restaurant)
    return db_restaurant


@app.get("/restaurants", response_model=list[RestaurantOut])
def get_restaurants(db: Session = Depends(get_db)):
    return db.query(Restaurant).all()

@app.get("/restaurants/{restaurant_id}", response_model=RestaurantOut)
def get_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    restaurant = (
        db.query(Restaurant)
        .filter(Restaurant.restaurant_id == restaurant_id)
        .first()
    )
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant


@app.put("/restaurants/{restaurant_id}", response_model=RestaurantOut)
def update_restaurant(
    restaurant_id: int,
    data: RestaurantCreate,
    db: Session = Depends(get_db)
):
    restaurant = db.query(Restaurant).get(restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    for key, value in data.dict().items():
        setattr(restaurant, key, value)

    db.commit()
    db.refresh(restaurant)
    return restaurant


@app.delete("/restaurants/{restaurant_id}")
def delete_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    restaurant = db.query(Restaurant).get(restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    db.delete(restaurant)
    db.commit()
    return {"message": "Restaurant deleted"}


@app.post("/menu-items", response_model=MenuItemOut)
def create_menu_item(
    item: MenuItemCreate,
    db: Session = Depends(get_db)
):
    restaurant = db.query(Restaurant).get(item.restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    db_item = MenuItem(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@app.get("/restaurants/{restaurant_id}/menu", response_model=list[MenuItemOut])
def get_menu_items(restaurant_id: int, db: Session = Depends(get_db)):
    return (
        db.query(MenuItem)
        .filter(MenuItem.restaurant_id == restaurant_id)
        .all()
    )


@app.put("/menu-items/{food_id}", response_model=MenuItemOut)
def update_menu_item(
    food_id: int,
    data: MenuItemCreate,
    db: Session = Depends(get_db)
):
    item = db.query(MenuItem).get(food_id)
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    for key, value in data.dict().items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)
    return item


@app.delete("/menu-items/{food_id}")
def delete_menu_item(food_id: int, db: Session = Depends(get_db)):
    item = db.query(MenuItem).get(food_id)
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    db.delete(item)
    db.commit()
    return {"message": "Menu item deleted"}


@app.post("/chat")
def chat(user_id: int, message: str, db: Session = Depends(get_db)):
    # ---- Kullanıcı bilgileri ----
    diets = (
        db.query(Diet.diet_name)
        .join(UserDiet)
        .filter(UserDiet.user_id == user_id)
        .all()
    )

    allergens = (
        db.query(Allergen.allergen_name)
        .join(UserAllergen)
        .filter(UserAllergen.user_id == user_id)
        .all()
    )

    preferences = (
        db.query(FoodPreference.preference_name)
        .join(UserFoodPreference)
        .filter(UserFoodPreference.user_id == user_id)
        .all()
    )

    diet_text = ", ".join([d[0] for d in diets]) or "Belirtilmemiş"
    preference_text = ", ".join([p[0] for p in preferences]) or "Belirtilmemiş"
    user_allergens = [a[0].lower() for a in allergens]

    # ---- MENU ----
    full_menu = get_full_menu(db)
    safe_menu = filter_menu_by_allergen(full_menu, user_allergens)

    if not safe_menu:
        return {
            "reply": "Maalesef alerjenlerine uygun yemek bulunamadı 😔"
        }

    menu_text = build_menu_text(safe_menu)

    # ---- PROMPT ----
    prompt = f"""
Kullanıcı bilgileri:
- Diyet: {diet_text}
- Sevdiği yemekler: {preference_text}

Aşağıda SADECE kullanıcının alerjenlerine UYGUN menü yer almaktadır:

{menu_text}

Kullanıcının mesajı:
"{message}"

Kurallar:
- Yalnızca yukarıdaki menüden seçim yap
- TEK bir yemek öner
- Restoran adını ve yemek adını belirt
- Kısa ve net açıkla
"""

    reply = ask_ollama(prompt)
    return {"reply": reply}
