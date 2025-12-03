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

    // Şimdilik sadece konsola basıyoruz,
    // backend hazır olduğunda buraya fetch/axios eklenebilir.
    console.log("Profil verileri:", {
      diets: formData.diets,
      allergens: formData.allergens,
      food_preferences: formData.foodPreferences,
    });
  }

  return (
    <div className="app-bg">
      <div className="profile-card">
        <h1 className="app-title">Meal Selector</h1>
        <p className="app-subtitle">
          Sana en uygun yemek önerilerini hazırlayabilmemiz için önce temel
          tercihlerini kaydedelim.
        </p>

        <form onSubmit={handleSubmit} className="profile-form">
          <section className="form-section">
            <h2 className="section-title">🍽️ Beslenme Şekli </h2>

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
                <span className="mono">vegan, gluten-free</span> gibi.
              </p>
            </div>
          </section>

          <section className="form-section">
            <h2 className="section-title">⚠️ Alerjenler <</h2>

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
                LLM bu alanı, sana öneri verirken pozitif ağırlık olarak
                kullanacak. Yine virgülle ayırabilirsin.
              </p>
            </div>
          </section>

          <button type="submit" className="submit-btn">
            Profili Kaydet
          </button>

          {status === "saved" && (
            <p className="status-text success">
              Profil kaydedildi (şimdilik sadece frontend tarafında). 🎉
            </p>
          )}
        </form>
      </div>
    </div>
  );
}

export default App;
