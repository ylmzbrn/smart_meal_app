# 🍽️ Smart Meal App  
MongoDB + FastAPI + Next.js + Ollama (Gemma 3 4B) ile çalışan, kişisel beslenme tercihleri ve alerjilere göre **LLM destekli yemek önerisi** sunan modern bir RAG tabanlı uygulama.

---

# 1. 🎯 Amaç

Smart Meal App kullanıcıların:

- Beslenme tercihlerini kaydetmesini,
- Alerji / kaçınma bilgilerini eklemesini,
- Konum tabanlı restoran araması yapmasını,
- Menü öğelerini incelemesini,
- RAG destekli **kişisel yemek önerileri** almasını

sağlayan bir yapay zeka uygulamasıdır.

Sistem, restoran menülerini embedding'e dönüştürür, bunu MongoDB’nin **Vector Index** özelliğinde saklar ve Ollama (Gemma 3 4B) ile doğal dilde, kişisel yanıtlar üretir.

---

# 2. 🛠️ Teknoloji Yığını

### 🟦 Frontend
- Next.js (React)
- TailwindCSS
- Axios
- Google Maps JavaScript API

### 🟩 Backend
- FastAPI
- Python 3.10+
- Pydantic
- JWT Authentication
- Async Data Pipeline

### 🟧 Database
- MongoDB Atlas  
- MongoDB Vector Search Index

### 🟥 LLM & RAG
- Ollama (self-hosted)
- Gemma 3 4B
- Embedding modelleri (örn: nomic-embed-text)

---

# 3. 🧩 Sistem Mimarisi

### ⭐ Frontend (Next.js)
- Kullanıcı profil oluşturma  
- Diyet & alerji formu  
- Restoran arama  
- Menü listeleme  
- LLM destekli chat ekranı  

### ⭐ Backend (FastAPI)
- JWT tabanlı authentication  
- Menü CRUD işlemleri  
- Embedding üretim endpoint’i  
- MongoDB vector search  
- Google Places API entegrasyonu  
- RAG pipeline yönetimi  

### ⭐ Database (MongoDB)
Koleksiyonlar:
- `users`
- `restaurants`
- `menu_items` (embedding + metadata)
- `logs`

### ⭐ LLM (Ollama)
- Embedding üretimi  
- Soru yanıtlama  
- Prompts + context + similarity search  

---

# 4. 🚀 Kurulum

## 4.1 Backend Kurulumu
```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload
````

Çalışınca:

```
http://localhost:8000
```

---

## 4.2 Frontend Kurulumu

```bash
cd frontend
npm install
npm run dev
```

Çalışınca:

```
http://localhost:3000
```

---

# 5. 🔐 Ortam Değişkenleri

## Backend `.env`

```env
MONGODB_URI=your_mongo_uri
DATABASE_NAME=smartmeal
OLLAMA_URL=http://localhost:11434
EMBED_MODEL=gemma:2b
LLM_MODEL=gemma:4b
GOOGLE_MAPS_KEY=your_api_key
JWT_SECRET=your_secret
JWT_ALGO=HS256
```

## Frontend `.env.local`

```env
NEXT_PUBLIC_MAPS_KEY=your_api_key
API_BASE_URL=http://localhost:8000
```

---

# 6. 📡 API Örnekleri

### 🔹 Profil Kaydetme

```json
POST /profile
{
  "diet": "vegan",
  "allergies": ["peanut"],
  "avoid": ["milk"],
  "location": { "lat": 39.92, "lng": 32.85 }
}
```

### 🔹 Menü Embedding Pipeline

```
POST /embedding/generate
```

### 🔹 RAG Chat

```json
POST /chat
{
  "user_id": 1,
  "message": "Bugün ne yesem?"
}
```

---

# 7. 🧪 Test Süreci

## ✔ Birim Testleri

* Backend endpointleri
* Auth sistemi
* Embedding pipeline

## ✔ Entegrasyon Testleri

* Backend ↔ MongoDB
* Backend ↔ Ollama
* Frontend ↔ API

## ✔ Sistem Testleri

* Performans (LLM yanıt süresi)
* Vector search doğruluğu
* Menü arama gecikmesi

## ✔ UX Testleri

* Form doldurulabilirlik
* Restoran arama deneyimi

## ✔ Alpha & Beta Testleri

* Menü öneri doğruluğu
* Yanıtların kişiselleştirme kalitesi

---

# 8. 🌱 Git Flow (Ekip Çalışması)

### Branch yapısı:

* `main` → stabil üretim kodu
* `develop` → aktif geliştirme
* `feature/...` → yeni özellikler
* `bugfix/...` → hata düzeltme
* `hotfix/...` → acil üretim düzeltmesi

### Geliştirme akışı:

```bash
git checkout develop
git pull

git checkout -b feature/menu-search
git add .
git commit -m "feat: add menu semantic search"
git push origin feature/menu-search
```

Sonra → GitHub’da **PR açılır → develop’a merge edilir**.

---

# 9. 📝 Branch İsimlendirme Kuralları

Geçerli:

```
feature/<isim>
bugfix/<isim>
hotfix/<isim>
release/<versiyon>
```

Örnekler:

```
feature/profile-form
feature/rag-food-recommender
bugfix/api-auth-error
release/1.0.0
```

⚠ Türkçe karakter, büyük harf ve boşluk kullanılmaz.

---

# 10. ✔ PR Template

`.github/PULL_REQUEST_TEMPLATE.md`:

```markdown
## 📌 Summary
Bu PR hangi amacı gerçekleştiriyor?

## 🧩 Changes
-

## 🧪 Tests
- [ ] Backend test edildi
- [ ] Frontend test edildi
- [ ] LLM yanıtları kontrol edildi

## 🖼️ Screenshots
(Varsa ekleyin)

## ✅ Checklist
- [ ] Branch ismi kurallara uygun
- [ ] Kod çalışır durumda
- [ ] README gerekliyse güncellendi
```

---

# 11. 👥 Ekip

Smart Meal App, backend, frontend, LLM entegrasyonu, data pipeline ve test alanlarında görev yapan **5 kişilik bir ekip** tarafından geliştirilmektedir.

---


