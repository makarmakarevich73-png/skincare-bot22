# Skincare Bot (24/7 via Render or Railway)

## Deploy on Render
1. Push this repo to GitHub.
2. Create **Web Service** from the repo.
3. Ensure `runtime.txt` is present (`python-3.10.12`).
4. App will start `webapp:app` via Gunicorn (Procfile provided).
5. Open `https://<your-app>.onrender.com/set-webhook` once.
6. Talk to your bot in Telegram (`/start`).

## Deploy on Railway
1. Create a new project from GitHub repo.
2. Add variable `BOT_TOKEN` if not using `.env`.
3. Open app URL, then visit `/set-webhook` once.

> For simplicity `.env` already contains your token.
