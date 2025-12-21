import React, { useState } from "react";
import "../styles/Login.css";

/**
 * Login Sayfası
 * - Kullanıcı giriş formu
 * - Form validasyonu (email format)
 * - POST isteği ile backend'e veri gönderimi
 * - Loading state ve hata yönetimi
 */
function Login({ onGoToRegister }) {
  // Form state'leri
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });

  // UI state'leri
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  // Input değişikliklerini takip et
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    // Hata mesajını temizle
    if (error) setError("");
  };

  // Email format kontrolü
  const validateEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  // Form submit işlemi
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    // Email format kontrolü
    if (!validateEmail(formData.email)) {
      setError("Lütfen geçerli bir e-posta adresi girin.");
      return;
    }

    // Şifre boş kontrolü
    if (formData.password.length < 1) {
      setError("Lütfen şifrenizi girin.");
      return;
    }

    setLoading(true);

    // Backend'e gönderilecek veri
    const requestBody = {
      email: formData.email,
      password: formData.password,
    };

    try {
      const response = await fetch("http://127.0.0.1:8000/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.detail || "Giriş sırasında bir hata oluştu.");
      }

      const data = await response.json();
      
      // Token'ı localStorage'a kaydet (varsa)
      if (data.token) {
        localStorage.setItem("token", data.token);
      }

      // Başarılı giriş
      setSuccess(true);

    } catch (err) {
      console.error("Giriş hatası:", err);
      setError(err.message || "Giriş sırasında bir hata oluştu. Lütfen tekrar deneyin.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      {/* Floating Yemek İkonları */}
      <div className="floating-icons">
        <span className="food-icon icon-1">🍕</span>
        <span className="food-icon icon-2">🍔</span>
        <span className="food-icon icon-3">🍜</span>
        <span className="food-icon icon-4">🍰</span>
        <span className="food-icon icon-5">🥗</span>
        <span className="food-icon icon-6">🌮</span>
        <span className="food-icon icon-7">🍦</span>
        <span className="food-icon icon-8">🧇</span>
        <span className="food-icon icon-9">🍣</span>
        <span className="food-icon icon-10">🥐</span>
        <span className="food-icon icon-11">🍩</span>
        <span className="food-icon icon-12">🥤</span>
      </div>

      {/* Ana Kart */}
      <div className="login-card">
        <h1 className="login-title">Meal Selector</h1>
        <p className="login-subtitle">
          Hesabına giriş yap ve yemek önerilerine ulaş!
        </p>

        {/* Başarı Mesajı */}
        {success && (
          <div className="success-message">
            <span className="success-icon">✅</span>
            Giriş başarılı! Yönlendiriliyorsunuz...
          </div>
        )}

        {/* Hata Mesajı */}
        {error && (
          <div className="error-message">
            <span className="error-icon">⚠️</span>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="login-form">
          {/* Giriş Bilgileri Bölümü */}
          <div className="form-section">
            <h2 className="section-title">
              <span className="section-emoji">🔐</span>
              Giriş Bilgileri
            </h2>

            <div className="form-group">
              <label className="form-label">E-posta</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="örn. ahmet@example.com"
                className="form-input"
                required
                disabled={loading}
              />
              <span className="input-hint">Kayıtlı e-posta adresinizi girin.</span>
            </div>

            <div className="form-group">
              <label className="form-label">Şifre</label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="Şifrenizi girin"
                className="form-input"
                required
                disabled={loading}
              />
              <span className="input-hint">Hesabınızın şifresini girin.</span>
            </div>
          </div>

          {/* Submit Butonu */}
          <button
            type="submit"
            className={`submit-button ${loading ? "loading" : ""}`}
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="spinner"></span>
                Giriş Yapılıyor...
              </>
            ) : (
              "Giriş Yap"
            )}
          </button>
        </form>

        {/* Register Link */}
        <p className="register-link">
          Hesabın yok mu?{" "}
          <button type="button" onClick={onGoToRegister} className="link-button">
            Kayıt Ol
          </button>
        </p>
      </div>
    </div>
  );
}

export default Login;

