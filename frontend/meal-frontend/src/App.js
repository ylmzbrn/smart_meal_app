import React, { useState } from "react";
import Register from "./pages/Register.js";
import Login from "./pages/Login.js";

/**
 * Ana Uygulama Bileşeni
 * Basit sayfa geçiş sistemi (şimdilik routing olmadan)
 */
function App() {
  const [currentPage, setCurrentPage] = useState("login");

  // Sayfa değiştirme fonksiyonu (child componentlere prop olarak geçilecek)
  const goToLogin = () => setCurrentPage("login");
  const goToRegister = () => setCurrentPage("register");

  return (
    <>
      {currentPage === "login" && <Login onGoToRegister={goToRegister} />}
      {currentPage === "register" && <Register onGoToLogin={goToLogin} />}
    </>
  );
}

export default App;
