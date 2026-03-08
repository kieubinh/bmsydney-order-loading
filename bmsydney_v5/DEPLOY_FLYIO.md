# Deploying BMSydney to Fly.io (Free)

Fly.io gives you a free always-on server with full Docker support,
meaning Tesseract OCR works perfectly.

---

## What you need
- A free Fly.io account: https://fly.io/app/sign-up
- A credit card (required by Fly.io, but you won't be charged on free tier)
- flyctl installed on your PC (the Fly.io command-line tool)

---

## Step 1 — Install flyctl on Windows

Open PowerShell and run:
```
iwr https://fly.io/install.ps1 -useb | iex
```

Then close and reopen PowerShell, and log in:
```
fly auth login
```
(This opens a browser to log in to your Fly.io account.)

---

## Step 2 — Edit fly.toml

Open `fly.toml` and change the app name to something unique:
```
app = "bmsydney-yourname"   ← change this to e.g. "bmsydney-john"
```

---

## Step 3 — Deploy for the first time

Extract the zip and open a terminal in the folder, then run:

```
fly launch --no-deploy
```

When asked:
- "Would you like to copy its configuration to the new app?" → Yes
- "Would you like to set up a Postgresql database?" → No
- "Would you like to set up an Upstash Redis database?" → No

Then create a persistent volume for your database and uploads:
```
fly volumes create bmsydney_data --size 1 --region syd
```

Then set a secret key (replace the value with anything random):
```
fly secrets set SECRET_KEY=change-this-to-something-random-abc123xyz
```

Now deploy:
```
fly deploy
```

This takes 3–5 minutes the first time (it builds the Docker image).
You'll see build logs scrolling. Wait for "✓ deployed successfully".

---

## Step 4 — Open your app

```
fly open
```

Or visit: https://bmsydney-yourname.fly.dev

You should see the BMSydney login page!

---

## Step 5 — Check it's working

```
fly logs
```

This shows the live server logs. Look for any errors.

---

## Updating the app later

Whenever you change app.py or templates, just run:
```
fly deploy
```

---

## Free tier limits (Fly.io)

- 3 shared-CPU VMs included free
- 256MB RAM per VM (we set 512MB — covered by free credits)
- 3GB total storage
- 160GB outbound bandwidth/month
- App stays running 24/7 (no sleeping!)
- Your URL: https://your-app-name.fly.dev

---

## Troubleshooting

| Problem | Fix |
|---|---|
| "App name already taken" | Change the name in fly.toml to something more unique |
| "No space left on device" | Run: fly volumes extend bmsydney_data --size 2 |
| Login page shows but can't log in | Run: fly ssh console -C "python3 -c 'from app import init_db; init_db()'" |
| 500 error | Run: fly logs — look for the Python traceback |
| OCR not working | Run: fly ssh console -C "tesseract --version" — should show v5.x |

---

## Alternative: Render.com (no OCR, but easiest)

If you don't need the image upload feature, Render.com is even simpler:

1. Push your code to GitHub
2. Go to render.com → New → Web Service → connect repo
3. Set:
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app`
4. Add environment variable: SECRET_KEY = anything-random
5. Deploy

Your app will be at: https://your-app-name.onrender.com
Note: it sleeps after 15 min inactivity on the free tier (30s to wake up).
