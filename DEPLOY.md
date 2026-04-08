# Deploy Air We Go — Step-by-Step Guide

Your app has two parts:
- **Backend:** Flask API (Python) — must run on a server that can execute Python.
- **Frontend:** React + Vite — build to static files and host on a static/CDN host.

You will deploy **backend** and **frontend** separately, then connect the frontend to the backend URL.

---

## Part 1: Prepare Your Code (Do This First)

### 1.1 Push your project to GitHub

1. Create a new repository on [github.com](https://github.com) (e.g. `air-we-go`). Do **not** add a README or .gitignore if your project already has them.
2. On your machine, open a terminal in the project folder (the one that contains `app.py` and `package.json`).
3. Run:

   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git push -u origin main
   ```

   Replace `YOUR_USERNAME` and `YOUR_REPO_NAME` with your GitHub username and repo name.

### 1.2 Ensure these are in `.gitignore`

You should **not** commit:

- `node_modules/`
- `venv/`, `.venv/`, `__pycache__/`
- `.env`
- `*.db`, `*.sqlite`
- `dist/`

If any are missing from `.gitignore`, add them before pushing.

---

## Part 2: Deploy the Backend (Flask API)

We use **Render** (free tier) as an example. You can use Railway or another host with the same idea.

### 2.1 Create a Render account and connect GitHub

1. Go to [https://render.com](https://render.com) and sign up (or log in).
2. Click **Connect account** and connect your **GitHub** account.
3. Allow Render to access the repository you created (e.g. `air-we-go`).

### 2.2 Create a new Web Service (backend)

1. In the Render dashboard, click **New +** → **Web Service**.
2. **Connect a repository:** select your repo (e.g. `air-we-go`). If you don’t see it, click **Configure account** and grant access.
3. Click **Connect**.

### 2.3 Configure the Web Service

Use these settings exactly (unless your repo is in a subfolder — see note below).

| Field | Value |
|--------|--------|
| **Name** | `air-we-go-api` (or any name you like) |
| **Region** | Choose closest to your users (e.g. Singapore) |
| **Branch** | `main` |
| **Root Directory** | Leave **empty** (your `app.py` is at the repo root) |
| **Runtime** | **Python 3** |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn -w 2 -b 0.0.0.0:$PORT wsgi:app` |

- **`$PORT`** is provided by Render; do not replace it.
- **`wsgi:app`** means: use the `app` object from the `wsgi` module (see `wsgi.py` in the repo).

### 2.4 Add environment variables (Backend)

In the same Web Service page, scroll to **Environment** (or **Environment Variables**).

Click **Add Environment Variable** and add:

| Key | Value |
|-----|--------|
| `FLASK_DEBUG` | `false` |
| `SECRET_KEY` | A long random string (e.g. generate one at [randomkeygen.com](https://randomkeygen.com) and pick a “CodeIgniter Encryption Keys” or 32+ character string) |
| `DEFAULT_CITY` | `Kuala Lumpur` |

Do **not** put your real `.env` file in the repo. Only set variables in Render’s UI.

### 2.5 Deploy the backend

1. Click **Create Web Service**.
2. Render will clone the repo, run `pip install -r requirements.txt`, then start gunicorn. Wait until the deploy finishes (green “Live” or “Deploy successful”).
3. At the top of the page you’ll see the service URL, e.g.:
   - `https://air-we-go-api.onrender.com`
4. Test the API in your browser:
   - Open: `https://YOUR-SERVICE-NAME.onrender.com/`
   - You should see something like: `{"status":"ok","service":"Air Quality Alert System"}`.

**Save this backend URL** — you will use it for the frontend in Part 3.

**Note:** On Render’s free tier, the service may “spin down” after inactivity. The first request after that can take 30–60 seconds; later requests are fast until it spins down again.

---

## Part 3: Deploy the Frontend (React + Vite)

We use **Vercel** (free tier) as an example. You can use Netlify with the same idea.

### 3.1 Create a Vercel account and import the repo

1. Go to [https://vercel.com](https://vercel.com) and sign up (or log in). Choose **Continue with GitHub**.
2. After logging in, click **Add New…** → **Project**.
3. **Import** the same GitHub repository you used for the backend (e.g. `air-we-go`). Click **Import**.

### 3.2 Configure the project (Frontend)

Vercel will detect the repo. Set:

| Field | Value |
|--------|--------|
| **Framework Preset** | **Vite** (should be auto-detected) |
| **Root Directory** | **`.`** or leave **empty** — your frontend (`package.json`, `vite.config.js`, `src/`, `index.html`) is at the repo root, not in a subfolder. |
| **Build Command** | `npm run build` |
| **Output Directory** | `dist` |
| **Install Command** | `npm install` (default) |

### 3.3 Set the API URL (Critical)

The frontend must call your **deployed** backend, not `localhost`.

1. Expand **Environment Variables**.
2. Add one variable:
   - **Name:** `VITE_API_URL`
   - **Value:** Your backend URL + `/api` (no trailing slash).  
     Example: `https://air-we-go-api.onrender.com/api`
3. Apply it to **Production**, **Preview**, and **Development** (or at least Production).

### 3.4 Deploy the frontend

1. Click **Deploy**.
2. Wait for the build to finish. Vercel will run `npm run build` and host the contents of `dist`.
3. When done, you’ll get a URL like: `https://air-we-go-xxxx.vercel.app`.

Open that URL in your browser. The app should load and show data from your Render backend (e.g. Kuala Lumpur AQI, forecast, seasonal).

---

## Part 4: Verify Everything

1. **Frontend:** Open your Vercel URL. Use the search bar to change the city (e.g. Penang). You should see AQI, forecast, and seasonal data update.
2. **Backend:** If something fails, open the backend health URL again: `https://YOUR-BACKEND.onrender.com/`. If that works, the backend is up; issues are likely CORS or `VITE_API_URL` (see below).

---

## Part 5: Optional — Custom Domain and CORS

- **Custom domain:** In Vercel: Project → **Settings** → **Domains**. In Render: Web Service → **Settings** → **Custom Domain**.
- **CORS:** The backend allows all origins for `/api/*`. For production you can restrict this in `app.py` to your frontend domain only (e.g. your Vercel URL) for extra security.

---

## Quick Reference

| What | Where |
|------|--------|
| Backend code | `app.py`, `routes/`, `services/`, `config.py`, `requirements.txt` |
| Frontend code | `src/`, `index.html`, `package.json`, `vite.config.js` |
| Backend URL (example) | `https://air-we-go-api.onrender.com` |
| Frontend env var | `VITE_API_URL` = `https://air-we-go-api.onrender.com/api` |
| Start command (backend) | `gunicorn -w 2 -b 0.0.0.0:$PORT wsgi:app` |
| Build (frontend) | `npm run build` → output in `dist/` |

---

## If Your Repo Structure Is Different

- If the **backend** is in a subfolder (e.g. `backend/`), set Render **Root Directory** to that folder and use a **Start Command** like:  
  `gunicorn -w 2 -b 0.0.0.0:$PORT wsgi:app`  
  (from that folder, so `app.py` must be there and named `app.py`.)
- If the **frontend** is in a subfolder (e.g. `frontend/`), set Vercel **Root Directory** to that folder so that `package.json` and `vite.config.js` are in the root of the build context.

---

## Troubleshooting

| Problem | What to check |
|--------|----------------|
| Frontend shows “Failed to fetch” or no data | 1) `VITE_API_URL` in Vercel = backend URL + `/api`. 2) Backend is “Live” on Render. 3) Open backend URL in browser: `https://xxx.onrender.com/` — should return JSON. |
| Backend deploy fails on Render | Check **Logs** for errors. Common: wrong **Start Command** (use `wsgi:app` and `$PORT`). Ensure `wsgi.py` exists in the repo. |
| Frontend build fails on Vercel | Check build logs. Ensure **Build Command** is `npm run build` and **Output Directory** is `dist`. |
| First request very slow | Normal on Render free tier (cold start). Next requests are fast until the service spins down again. |
| **Frontend shows “UPDATE DELAYED”** | Backend could not get data from Open-Meteo (geocoding or AQ requests failed/timed out on Render). 1) In Render dashboard open your service → **Logs**. Look for `Geocoding failed` or `Open-Meteo AQ request failed` or `UPDATE_DELAYED: all grid points failed`. 2) Wait 30–60 s and try again (cold start or Open-Meteo slow). 3) Code now uses 20s timeouts for Open-Meteo; redeploy backend so the change is live. |

You’re done. Your app is deployed: backend on Render, frontend on Vercel, talking to each other via `VITE_API_URL`.
