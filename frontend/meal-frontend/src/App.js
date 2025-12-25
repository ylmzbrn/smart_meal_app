import React, { useState } from "react";
import "./App.css";

import Register from "./pages/Register";
import Login from "./pages/Login";
import Chat from "./pages/Chat";

const API_BASE_URL =
  process.env.REACT_APP_API_BASE_URL || "http://localhost:8000";

function App() {
  // "login" | "register" | "profile" | "chat"
  const [currentPage, setCurrentPage] = useState("login");

  // Logged-in user
  const [currentUser, setCurrentUser] = useState(null);

  // ---- NAV HELPERS ----
  const goToLogin = () => {
    setCurrentUser(null);
    setCurrentPage("login");
  };

  const goToRegister = () => setCurrentPage("register");
  const goToProfile = () => setCurrentPage("profile");
  const goToChat = () => setCurrentPage("chat");

  // ---- LOGIN SUCCESS ----
  const handleLoginSuccess = (userData) => {
    setCurrentUser(userData);
    setCurrentPage("profile");
  };

  // ---- PROFILE FORM STATE ----
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

  // ---- PROFILE SUBMIT ----
  async function handleSubmit(e) {
    e.preventDefault();
    setStatus(null);
    setErrorMsg("");

    const payload = {
      user_id: currentUser?.user_id || null,
      diets: formData.diets,
      allergens: formData.allergens,
      food_preferences: formData.foodPreferences,
    };

    try {
      const res = await fetch(`${API_BASE_URL}/profile`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const text = await res.text();

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${text}`);
      }

      setStatus("saved");

      // ✅ AFTER PROFILE → CHAT
      setTimeout(() => {
        setCurrentPage("chat");
      }, 600);

    } catch (err) {
      setStatus("error");
      setErrorMsg(err.message || "Unknown error");
    }
  }

  // ---- EMOJI BACKGROUND ----
  const emojiList = [
    "🍕","🍔","🍟","🌭","🍣","🍤","🍜","🥗","🥙","🌮","🌯","🥐",
    "🍩","🍪","🍰","🧁","🍦","🍧","🍨","🍎","🍉","🍇","🍓","🍊",
    "🥑","🥥","🍞","🧀","🥨","🥟","🍱","🍛","🍙","🍘","🍝","🧇"
  ];

  const repeatedEmojis = Array.from({ length: 240 }, (_, i) => (
    <span key={i}>{emojiList[i % emojiList.length]}</span>
  ));

  // ---- PAGE SWITCH ----
  if (currentPage === "login") {
    return (
      <Login
        onGoToRegister={goToRegister}
        onLoginSuccess={handleLoginSuccess}
        API_BASE_URL={API_BASE_URL}
      />
    );
  }

  if (currentPage === "register") {
    return (
      <Register
        onGoToLogin={goToLogin}
        onRegisterSuccess={goToLogin}
        API_BASE_URL={API_BASE_URL}
      />
    );
  }

  if (currentPage === "chat") {
    return (
      <Chat
        currentUser={currentUser}
        API_BASE_URL={API_BASE_URL}
        onLogout={goToLogin}
      />
    );
  }

  // ---- PROFILE PAGE (DEFAULT) ----
  return (
    <div className="app-bg">
      <div className="emoji-bg" aria-hidden="true">
        {repeatedEmojis}
      </div>

      <div className="profile-card">
        <h1 className="app-title">Meal Selector</h1>

        {currentUser && (
          <p style={{ textAlign: "center", color: "#4a90d9", fontWeight: 600 }}>
            Hoş geldin, {currentUser.username}! 👋
          </p>
        )}

        <p className="app-subtitle">
          Sana uygun yemek önerileri için tercihlerini kaydedelim.
        </p>

        <form onSubmit={handleSubmit} className="profile-form">
          <div className="form-group">
            <label>Beslenme Şekli</label>
            <input
              type="text"
              name="diets"
              value={formData.diets}
              onChange={handleChange}
              placeholder="vegan, glutensiz"
            />
          </div>

          <div className="form-group">
            <label>Alerjenler</label>
            <input
              type="text"
              name="allergens"
              value={formData.allergens}
              onChange={handleChange}
              placeholder="fıstık, karides"
            />
          </div>

          <div className="form-group">
            <label>Sevdiğin Yiyecekler</label>
            <input
              type="text"
              name="foodPreferences"
              value={formData.foodPreferences}
              onChange={handleChange}
              placeholder="pizza, sushi"
            />
          </div>

          <button type="submit">Profili Kaydet</button>

          {status === "saved" && (
            <p style={{ color: "green" }}>Profil kaydedildi 🎉</p>
          )}

          {status === "error" && (
            <p style={{ color: "crimson" }}>
              Hata ❌ {errorMsg}
            </p>
          )}
        </form>
      </div>
    </div>
  );
}

export default App;
