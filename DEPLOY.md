# Deployment Guide

## Architecture

- **Frontend (React)** → Vercel (free, static hosting)
- **Backend (FastAPI + CrewAI)** → Railway (supports heavy Python, no timeout limits)

---

## Step 1: Push Code to GitHub

```bash
cd ~/Desktop/finance-agent-orchestration
git add -A
git commit -m "deployment ready"
git push origin main
```

If you haven't set up a remote yet:
```bash
gh repo create finance-agent-orchestration --public --source=. --push
```

---

## Step 2: Deploy Backend on Railway

1. Go to https://railway.app and sign in with GitHub

2. Click **"New Project"** → **"Deploy from GitHub Repo"**

3. Select your `finance-agent-orchestration` repo

4. Railway will detect the `Dockerfile`. If it asks, confirm:
   - **Root Directory:** `/` (repo root)
   - **Builder:** Dockerfile

5. Once deployed, go to **Settings → Networking → Generate Domain**
   - You'll get a URL like: `https://finance-agent-orchestration-production-xxxx.up.railway.app`
   - Save this URL, you'll need it for Step 3

6. Go to **Variables** tab and add these:

   | Variable | Value |
   |----------|-------|
   | `CEREBRAS_API_KEY` | `csk-ke8phxty9d34xp4jkdxjketnyr3d3wxpmvtnmmfey6y2mmk6` |
   | `CEREBRAS_MODEL` | `llama-4-scout-17b-16e-instruct` |
   | `ALPHA_VANTAGE_API_KEY` | `7M81POUXLKV6HYYE` |
   | `KITE_API_KEY` | Your Zerodha API key |
   | `KITE_API_SECRET` | Your Zerodha API secret |
   | `KITE_ACCESS_TOKEN` | (leave empty for now) |
   | `FRONTEND_URL` | (add after Step 3, your Vercel URL) |

7. Wait for the build to complete (3-5 min first time)

8. Test: visit `https://your-railway-url/api/health` — you should see:
   ```json
   {"status":"healthy","cerebras_configured":true,"zerodha_configured":false,"alpha_vantage_configured":true}
   ```

---

## Step 3: Deploy Frontend on Vercel

1. Go to https://vercel.com/new

2. Click **"Import"** → select your `finance-agent-orchestration` repo

3. Configure:
   - **Framework Preset:** Other
   - **Root Directory:** `.` (leave default)
   - Build & Output settings will be read from `vercel.json` automatically

4. Add **Environment Variable**:

   | Variable | Value |
   |----------|-------|
   | `VITE_API_URL` | `https://your-railway-url.up.railway.app` (from Step 2) |

5. Click **Deploy**

6. Once deployed, copy your Vercel URL (e.g., `https://finance-agent-orchestration.vercel.app`)

7. Go back to Railway → Variables → set:
   - `FRONTEND_URL` = `https://finance-agent-orchestration.vercel.app`

---

## Step 4: Configure Zerodha Kite Connect

1. Go to https://developers.kite.trade → your app settings

2. Set these URLs:
   - **Redirect URL:** `https://your-vercel-app.vercel.app/zerodha/callback`
   - **Postback URL:** `https://your-railway-url.up.railway.app/api/zerodha/postback`

3. To generate an access token:
   - Open: `https://your-railway-url.up.railway.app/api/zerodha/login`
   - It returns a login URL → open it in browser
   - Log in with your Zerodha credentials
   - You'll be redirected to your frontend callback page
   - The token exchange happens automatically

---

## Step 5: Verify Everything Works

1. Open your Vercel URL in a browser
2. The status bar should show green dots for Cerebras and Alpha Vantage
3. Type an investment goal, set amount and risk, click "Generate Investment Plan"
4. Wait 1-3 minutes for the 4 agents to complete their analysis

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Frontend shows "Backend not connected" | Check `VITE_API_URL` is set correctly in Vercel env vars. Redeploy after changing. |
| Railway build fails | Check build logs. Usually a dependency issue — make sure Python 3.12 is used. |
| CORS error in browser | Make sure `FRONTEND_URL` is set in Railway env vars. |
| `/api/invest` times out | Railway free tier has no timeout. Check Railway logs for errors. |
| Zerodha not working | Access token expires daily at 6 AM IST. Re-authenticate each morning. |

---

## Updating After Changes

```bash
git add -A
git commit -m "your change description"
git push origin main
```

Both Railway and Vercel auto-deploy on push to main.

---

## Cost

| Service | Free Tier |
|---------|-----------|
| **Vercel** | Unlimited for static sites |
| **Railway** | $5 free credit/month (enough for light use) |
| **Cerebras** | Free tier with rate limits |
| **Alpha Vantage** | 25 requests/day free |
| **Zerodha Kite** | ₹2000/month for API access |
