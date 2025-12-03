import React, { useState } from "react";
import "./App.css";

function App() {
  const [formData, setFormData] = useState({
    diets: "",
    allergens: "",
    foodPreferences: "",
  });

  const [status, setStatus] = useState(null);

  function handleChange(e) {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  }

  function handleSubmit(e) {
    e.preventDefault();
    setStatus("saved");

    console.log("Profil verileri:", {
      diets: formData.diets,
      allergens: formData.allergens,
      food_preferences: formData.foodPreferences,
    });
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

  return (
    <div className="app-bg">
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
              Profil kaydedildi! 🎉 (Şimdilik sadece frontend)
            </p>
          )}
        </form>
      </div>
    </div>
  );
}

export default App;
