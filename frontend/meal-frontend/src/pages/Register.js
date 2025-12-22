import React, { useState } from "react";
import "../styles/Register.css";

/**
 * Register Sayfası
 * - Kullanıcı kayıt formu
 * - Form validasyonu (email format, şifre eşleşme)
 * - POST isteği ile backend'e veri gönderimi
 * - Loading state ve hata yönetimi
 */
function Register({ onGoToLogin }) {
  // Form state'leri
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    passwordConfirm: "",
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

    // Şifre eşleşme kontrolü
    if (formData.password !== formData.passwordConfirm) {
      setError("Şifreler eşleşmiyor. Lütfen kontrol edin.");
      return;
    }

    // Şifre uzunluk kontrolü
    if (formData.password.length < 6) {
      setError("Şifre en az 6 karakter olmalıdır.");
      return;
    }

    setLoading(true);

    // Backend'e gönderilecek veri
    const requestBody = {
      name: formData.name,
      email: formData.email,
      password: formData.password,
    };

    try {
      const response = await fetch("http://127.0.0.1:8000/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.detail || "Kayıt sırasında bir hata oluştu.");
      }

      // Başarılı kayıt
      setSuccess(true);
      
      // Form'u temizle
      setFormData({
        name: "",
        email: "",
        password: "",
        passwordConfirm: "",
      });

    } catch (err) {
      console.error("Kayıt hatası:", err);
      setError(err.message || "Kayıt sırasında bir hata oluştu. Lütfen tekrar deneyin.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="register-page">
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
      <div className="register-card">
        <h1 className="register-title">Meal Selector</h1>
        <p className="register-subtitle">
          Hesabını oluştur ve kişiselleştirilmiş yemek önerilerine ulaş!
        </p>

        {/* Başarı Mesajı */}
        {success && (
          <div className="success-message">
            <span className="success-icon">✅</span>
            Kayıt başarılı! Giriş yapabilirsiniz.
          </div>
        )}

        {/* Hata Mesajı */}
        {error && (
          <div className="error-message">
            <span className="error-icon">⚠️</span>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="register-form">
          {/* Kişisel Bilgiler Bölümü */}
          <div className="form-section">
            <h2 className="section-title">
              <span className="section-emoji">👤</span>
              Kişisel Bilgiler
            </h2>

            <div className="form-group">
              <label className="form-label">Ad Soyad</label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                placeholder="örn. Ahmet Yılmaz"
                className="form-input"
                required
                disabled={loading}
              />
              <span className="input-hint">Tam adınızı girin.</span>
            </div>

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
              <span className="input-hint">Geçerli bir e-posta adresi girin.</span>
            </div>
          </div>

          {/* Güvenlik Bölümü */}
          <div className="form-section">
            <h2 className="section-title">
              <span className="section-emoji">🔒</span>
              Güvenlik
            </h2>

            <div className="form-group">
              <label className="form-label">Şifre</label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="En az 6 karakter"
                className="form-input"
                required
                minLength={6}
                disabled={loading}
              />
              <span className="input-hint">Güçlü bir şifre seçin (en az 6 karakter).</span>
            </div>

            <div className="form-group">
              <label className="form-label">Şifre Tekrar</label>
              <input
                type="password"
                name="passwordConfirm"
                value={formData.passwordConfirm}
                onChange={handleChange}
                placeholder="Şifrenizi tekrar girin"
                className="form-input"
                required
                minLength={6}
                disabled={loading}
              />
              <span className="input-hint">Şifrenizi doğrulamak için tekrar girin.</span>
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
                Kaydediliyor...
              </>
            ) : (
              "Kayıt Ol"
            )}
          </button>
        </form>

        {/* Login Link */}
        <p className="login-link">
          Zaten hesabın var mı?{" "}
          <button type="button" onClick={onGoToLogin} className="link-button">
            Giriş Yap
          </button>
        </p>
      </div>
    </div>
  );
}

export default Register;
