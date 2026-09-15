# 🌐 Deploying Latha PG Manager to a 24/7 Online Cloud Server (Free)

This guide shows you how to host the **Latha PG Manager** online in the cloud so you can use it on your phone anytime, anywhere in the world, **without keeping your PC turned on**.

---

## 🚀 Option 1: Render.com (Recommended — 100% Free & Zero-Config)

Render connects directly to your GitHub repository and automatically deploys the FastAPI backend and web dashboard.

### Step 1: Sign in to Render
1. Go to [https://dashboard.render.com/register](https://dashboard.render.com/register).
2. Click **"Continue with GitHub"** and log in with your GitHub account (`pavankalyan39015-a11y`).

### Step 2: Create a New Web Service
1. On the Render Dashboard, click the blue **"New +"** button in the top-right corner.
2. Select **"Web Service"**.
3. Choose **"Build and deploy from a Git repository"** and click **Next**.
4. In the list of repositories, find **`latha-pg`** and click **Connect**.

### Step 3: Configure Service Details
Fill in the following fields (most are filled automatically):
- **Name**: `latha-pg` (or your preferred name)
- **Region**: Choose the closest region (e.g., *Singapore* or *Frankfurt*)
- **Branch**: `main`
- **Runtime**: `Python 3`
- **Build Command**: 
  ```bash
  pip install -r requirements.txt && python seed_data.py
  ```
- **Start Command**: 
  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```
- **Instance Type**: Select **Free** ($0 / month)

### Step 4: Deploy!
1. Click **"Deploy Web Service"** at the bottom.
2. Wait ~2 minutes while Render installs dependencies and initializes the database.
3. Once the status shows **Live**, Render gives you your permanent online URL:
   `https://latha-pg-xxxx.onrender.com`

---

## 📱 How to Use on Your Phone Once Deployed

### Method A: Instant Mobile App (PWA)
1. Open your online URL on your phone in **Google Chrome**:
   `https://your-service-name.onrender.com/dashboard/`
2. Tap the amber **"Install App"** button at the top header (or tap Chrome menu `⋮` -> **"Install app"** / **"Add to Home screen"**).
3. The app is now installed on your phone home screen, running 24/7 from the cloud!

### Method B: Native Android APK
1. Open the **Latha PG** APK app on your phone.
2. Tap the **Settings (Gear icon)** in the top right.
3. Enter your online Render URL:
   `https://your-service-name.onrender.com/dashboard/`
4. Tap **Save & Connect**. The app will now connect permanently to your online server.

---

## 🔄 Automatic Updates
Whenever you push changes or new features to your GitHub repository `https://github.com/pavankalyan39015-a11y/latha-pg`, Render will automatically rebuild and deploy the new version!
