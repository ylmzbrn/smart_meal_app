"""
Veritabanı içeriğini görüntüleme scripti
Kullanım: python view_db.py
"""
from database import SessionLocal
from models import User, Diet, Allergen, FoodPreference, UserDiet, UserAllergen, UserFoodPreference

db = SessionLocal()

print("=" * 50)
print("USER TABLOSU")
print("=" * 50)
users = db.query(User).all()
for u in users:
    print(f"  ID: {u.user_id} | {u.username} | {u.email}")
print(f"  Toplam: {len(users)} kullanıcı\n")

print("=" * 50)
print("DIET TABLOSU")
print("=" * 50)
diets = db.query(Diet).all()
for d in diets:
    print(f"  ID: {d.diet_id} | {d.diet_name}")
print(f"  Toplam: {len(diets)} diyet\n")

print("=" * 50)
print("ALLERGEN TABLOSU")
print("=" * 50)
allergens = db.query(Allergen).all()
for a in allergens:
    print(f"  ID: {a.allergen_id} | {a.allergen_name}")
print(f"  Toplam: {len(allergens)} alerjen\n")

print("=" * 50)
print("FOODPREFERENCE TABLOSU")
print("=" * 50)
foods = db.query(FoodPreference).all()
for f in foods:
    print(f"  ID: {f.preference_id} | {f.preference_name}")
print(f"  Toplam: {len(foods)} yiyecek tercihi\n")

print("=" * 50)
print("KULLANICI - DİYET İLİŞKİLERİ (userdiet)")
print("=" * 50)
user_diets = db.query(UserDiet).all()
for ud in user_diets:
    user = db.query(User).filter(User.user_id == ud.user_id).first()
    diet = db.query(Diet).filter(Diet.diet_id == ud.diet_id).first()
    print(f"  {user.username if user else '?'} -> {diet.diet_name if diet else '?'}")
print(f"  Toplam: {len(user_diets)} ilişki\n")

print("=" * 50)
print("KULLANICI - ALERJEN İLİŞKİLERİ (userallergen)")
print("=" * 50)
user_allergens = db.query(UserAllergen).all()
for ua in user_allergens:
    user = db.query(User).filter(User.user_id == ua.user_id).first()
    allergen = db.query(Allergen).filter(Allergen.allergen_id == ua.allergen_id).first()
    print(f"  {user.username if user else '?'} -> {allergen.allergen_name if allergen else '?'}")
print(f"  Toplam: {len(user_allergens)} ilişki\n")

print("=" * 50)
print("KULLANICI - YİYECEK TERCİHİ İLİŞKİLERİ (userfoodpreference)")
print("=" * 50)
user_foods = db.query(UserFoodPreference).all()
for uf in user_foods:
    user = db.query(User).filter(User.user_id == uf.user_id).first()
    food = db.query(FoodPreference).filter(FoodPreference.preference_id == uf.preference_id).first()
    print(f"  {user.username if user else '?'} -> {food.preference_name if food else '?'}")
print(f"  Toplam: {len(user_foods)} ilişki\n")

db.close()
print("✅ Veritabanı kontrolü tamamlandı!")

