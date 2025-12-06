import React from "react";

export default function MainLayout({ currentScreen, onNavigate, children }) {
  return (
    <div className="app-shell">
      <header className="app-header">
        <h1>Biblical Therapy Assistant</h1>
        <nav>
          <button onClick={() => onNavigate("home")}>Home</button>
          <button onClick={() => onNavigate("settings")}>Settings</button>
        </nav>
      </header>
      <main className="app-main">{children}</main>
      <footer className="app-footer">
        MVP Frontend • Scripture search & verse exploration
      </footer>
    </div>
  );
}