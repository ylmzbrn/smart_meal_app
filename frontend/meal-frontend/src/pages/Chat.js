import React, { useState } from "react";
import "../App.css"; // App.css is still reused

function Chat({ currentUser, API_BASE_URL, onLogout }) {
  const [messages, setMessages] = useState([
    { sender: "bot", text: "Hoş geldin! Bugün ne yemek istersin? 🍽️" },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const emojiList = [
    "🍕","🍔","🍟","🌭","🍣","🍤","🍜","🥗","🥙","🌮","🌯","🥐",
    "🍩","🍪","🍰","🧁","🍦","🍧","🍨","🍎","🍉","🍇","🍓","🍊",
    "🥑","🥥","🍞","🧀","🥨","🥟","🍱","🍛","🍙","🍘","🍝","🧇"
  ];

  const repeatedEmojis = Array.from({ length: 240 }, (_, i) => (
    <span key={i}>{emojiList[i % emojiList.length]}</span>
  ));

  // 🔹 CHAT GÖNDERME
  async function handleSend(e) {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userText = input;

    setMessages((prev) => [
      ...prev,
      { sender: "user", text: userText },
    ]);

    setInput("");
    setLoading(true);

    try {
      const response = await fetch(
        `${API_BASE_URL}/chat?user_id=${currentUser?.user_id}&message=${encodeURIComponent(
          userText
        )}`,
        { method: "POST" }
      );

      const data = await response.json();

      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: data.reply },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text: "Bir hata oluştu 😢 Lütfen tekrar dene.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app-bg">
      {/* LOGOUT */}
      <div style={{ position: "fixed", top: 12, left: 12, zIndex: 10 }}>
        <button
          onClick={onLogout}
          style={{
            padding: "8px 12px",
            borderRadius: 10,
            border: "1px solid rgba(0,0,0,0.15)",
            background: "white",
            cursor: "pointer",
          }}
        >
          ← Logout
        </button>
      </div>

      {/* EMOJI BACKGROUND */}
      <div className="emoji-bg" aria-hidden="true">
        {repeatedEmojis}
      </div>

      {/* CHAT CARD */}
      <div className="chat-card">
        <h1 className="app-title">Meal Selector Chat</h1>
        <p className="app-subtitle">
          Ne yemek istediğini yaz, sana özel önerelim 🍽️
        </p>

        {/* CHAT WINDOW */}
        <div className="chat-window">
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`chat-message ${
                msg.sender === "user" ? "user" : "bot"
              }`}
            >
              {msg.text}
            </div>
          ))}

          {loading && (
            <div className="chat-message bot">
              Yazıyor... ✍️
            </div>
          )}
        </div>

        {/* INPUT */}
        <form onSubmit={handleSend} className="chat-input-area">
          <input
            type="text"
            placeholder="Bir şey yaz..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
          />
          <button type="submit" disabled={loading}>
            Gönder
          </button>
        </form>
      </div>
    </div>
  );
}

export default Chat;
