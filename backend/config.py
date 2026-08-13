import os

# ===== TELEGRAM =====
BOT_TOKEN = "8949405030:AAEmxY9OyLqUDs8S1mmHccSUMPvmcgG4o_k"
ADMIN_ID = 7935943057
SUPPORT_LINK = "https://t.me/ваш_username_bot"

# ===== FLASK =====
SECRET_KEY = os.environ.get("SECRET_KEY", "s3cr3t_k3y_2026_blackbit")
DEBUG = os.environ.get("DEBUG", "False") == "True"

# ===== DATABASE =====
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///blackbit.db")

# ===== CORS (для GitHub Pages) =====
CORS_ORIGINS = [
    "https://g87291707-crypto.github.io",
    "http://localhost:5500",
    "http://127.0.0.1:5500"
]
