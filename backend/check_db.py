"""
Veritabanı tablo yapısını kontrol eden script
"""
from database import engine
from sqlalchemy import inspect

inspector = inspect(engine)

# Tüm tabloları listele
print("=== MEVCUT TABLOLAR ===")
tables = inspector.get_table_names()
for table in tables:
    print(f"  - {table}")

print("\n=== USER TABLOSU KOLONLARI ===")
try:
    columns = inspector.get_columns("User")
    for col in columns:
        print(f"  - {col['name']}: {col['type']}")
except Exception as e:
    print(f"  Hata: {e}")

print("\n=== diet TABLOSU KOLONLARI ===")
try:
    columns = inspector.get_columns("diet")
    for col in columns:
        print(f"  - {col['name']}: {col['type']}")
except Exception as e:
    print(f"  Hata: {e}")

print("\n=== allergen TABLOSU KOLONLARI ===")
try:
    columns = inspector.get_columns("allergen")
    for col in columns:
        print(f"  - {col['name']}: {col['type']}")
except Exception as e:
    print(f"  Hata: {e}")

print("\n=== userdiet TABLOSU KOLONLARI ===")
try:
    columns = inspector.get_columns("userdiet")
    for col in columns:
        print(f"  - {col['name']}: {col['type']}")
except Exception as e:
    print(f"  Hata: {e}")

print("\n=== foodpreference TABLOSU KOLONLARI ===")
try:
    columns = inspector.get_columns("foodpreference")
    for col in columns:
        print(f"  - {col['name']}: {col['type']}")
except Exception as e:
    print(f"  Hata: {e}")

print("\n=== userfoodpreference TABLOSU KOLONLARI ===")
try:
    columns = inspector.get_columns("userfoodpreference")
    for col in columns:
        print(f"  - {col['name']}: {col['type']}")
except Exception as e:
    print(f"  Hata: {e}")

print("\n=== userallergen TABLOSU KOLONLARI ===")
try:
    columns = inspector.get_columns("userallergen")
    for col in columns:
        print(f"  - {col['name']}: {col['type']}")
except Exception as e:
    print(f"  Hata: {e}")

