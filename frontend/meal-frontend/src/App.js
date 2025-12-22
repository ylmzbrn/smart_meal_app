import React, { useState } from "react";
import "./App.css";

import Register from "./pages/Register.js";
import Login from "./pages/Login.js";

const API_BASE_URL =
  process.env.REACT_APP_API_BASE_URL || "http://localhost:8000";

function App() {
  // "login" | "register" | "profile"
  const [currentPage, setCurrentPage] = useState("login");

  const goToLogin = () => setCurrentPage("login");
  const goToRegister = () => setCurrentPage("register");
  const goToProfile = () => setCurrentPage("profile");

  const [formData, setFormData] = useState({
    diets: "",
    allergens: "",
    foodPreferences: "",
  });

  // status: null | "saved" | "error"
  const [status, setStatus] = useState(null);
  const [errorMsg, setErrorMsg] = useState("");

  function handleChange(e) {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  }

  // ✅ Backend'e POST atan gerçek submit
  async function handleSubmit(e) {
    e.preventDefault();
    setStatus(null);
    setErrorMsg("");

    // Backend /profile için payload (snake_case)
    const payload = {
      diets: formData.diets,
      allergens: formData.allergens,
      food_preferences: formData.foodPreferences,
    };

    console.log("Gönderilen payload:", payload);

    try {
      const res = await fetch(`${API_BASE_URL}/profile`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const text = await res.text(); // debug için önce text

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${text}`);
      }

      let data = {};
      try {
        data = JSON.parse(text);
      } catch {
        data = { raw: text };
      }

      console.log("Backend response:", data);
      setStatus("saved");

      // İstersen profil kaydedince chat sayfasına vs geçirebilirsin
      // şimdilik profile ekranında kalıyoruz.
    } catch (err) {
      console.error("Profil kaydetme hatası:", err);
      setErrorMsg(err?.message || "Bilinmeyen hata");
      setStatus("error");
    }
  }

  // --- EMOJILERI OLUŞTURAN KOD ---
  const emojiList = [
    "🍕","🍔","🍟","🌭","🍣","🍤","🍜","🥗","🥙","🌮","🌯","🥐",
    "🍩","🍪","🍰","🧁","🍦","🍧","🍨","🍎","🍉","🍇","🍓","🍊",
    "🥑","🥥","🍞","🧀","🥨","🥟","🍱","🍛","🍙","🍘","🍝","🧇"
  ];

  const repeatedEmojis = Array.from({ length: 240 }, (_, i) => (
    <span key={i}>{emojiList[i % emojiList.length]}</span>
  ));

  // ---- SAYFA SWITCH ----
  if (currentPage === "login") {
    return (
      <Login
        onGoToRegister={goToRegister}
        // Login başarılı olunca profile geçmek istersen:
        onLoginSuccess={goToProfile}
        API_BASE_URL={API_BASE_URL}
      />
    );
  }

  if (currentPage === "register") {
    return (
      <Register
        onGoToLogin={goToLogin}
        // Register başarılı olunca login'e dönmek istersen:
        onRegisterSuccess={goToLogin}
        API_BASE_URL={API_BASE_URL}
      />
    );
  }

  // default: profile
  return (
    <div className="app-bg">
      {/* Üste mini nav koyduk: login'e dönmek istersen */}
      <div style={{ position: "fixed", top: 12, left: 12, zIndex: 10 }}>
        <button
          type="button"
          onClick={goToLogin}
          style={{
            padding: "8px 12px",
            borderRadius: 10,
            border: "1px solid rgba(0,0,0,0.15)",
            background: "white",
            cursor: "pointer",
          }}
        >
          ← Login
        </button>
      </div>

      {/* === EMOJI BACKGROUND LAYER === */}
      <div className="emoji-bg" aria-hidden="true">
        {repeatedEmojis}
      </div>

      {/* === MAIN CARD (BAŞLIK + FORM) === */}
      <div className="profile-card">
        <div className="title-wrapper">
          <h1 className="app-title">Meal Selector</h1>
          <p className="app-subtitle">
            Sana en uygun yemek önerilerini hazırlayabilmemiz için önce temel
            tercihlerini kaydedelim.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="profile-form">
          {/* BESLENME */}
          <section className="form-section">
            <h2 className="section-title">🍽️ Beslenme Şekli</h2>

            <div className="form-group">
              <label>Beslenme Şeklin</label>
              <input
                type="text"
                name="diets"
                placeholder="örn. vegan, glutensiz, düşük karbonhidrat"
                value={formData.diets}
                onChange={handleChange}
              />
              <p className="help-text">
                Birden fazla yazacaksan virgülle ayır:{" "}
                <span className="mono">vegan, gluten-free</span>.
              </p>
            </div>
          </section>

          {/* ALERJENLER */}
          <section className="form-section">
            <h2 className="section-title">⚠️ Alerjenler</h2>

            <div className="form-group">
              <label>Alerjin Olan Yiyecekler</label>
              <input
                type="text"
                name="allergens"
                placeholder="örn. fıstık, ceviz, karides"
                value={formData.allergens}
                onChange={handleChange}
              />
              <p className="help-text">
                Tıbben tüketmemen gereken yiyecekleri virgülle ayırarak yaz.
              </p>
            </div>
          </section>

          {/* TERCİH ETTİĞİN YİYECEKLER */}
          <section className="form-section">
            <h2 className="section-title">❤️ Tercih Ettiğin Yiyecekler</h2>

            <div className="form-group">
              <label>En Çok Sevdiğin Yemekler / Yiyecekler</label>
              <input
                type="text"
                name="foodPreferences"
                placeholder="örn. sushi, pizza, mercimek çorbası"
                value={formData.foodPreferences}
                onChange={handleChange}
              />
              <p className="help-text">
                LLM bu alanı önerileri iyileştirmek için pozitif ağırlık olarak
                kullanacak. Virgülle ayırabilirsin.
              </p>
            </div>
          </section>

          <button type="submit" className="submit-btn">
            Profili Kaydet
          </button>

          {status === "saved" && (
            <p className="status-text success">
              Profil kaydedildi! 🎉 (backend’e gönderildi)
            </p>
          )}

          {status === "error" && (
            <p className="status-text" style={{ color: "crimson" }}>
              Profil kaydedilemedi ❌ {errorMsg ? `— ${errorMsg}` : ""}
            </p>
          )}
        </form>
      </div>
    </div>
  );
}

export default App;
