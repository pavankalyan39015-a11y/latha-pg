# 📱 Mobile App & APK Guide for Latha PG Accommodation Manager

This guide explains how to get and install the **Latha PG Manager** app on your Android smartphone.

---

## ⚡ Method 1: Instant Mobile App Install (Recommended — Takes 10 Seconds)

You do **not** need to compile an APK to get a full native mobile app experience! Thanks to **Progressive Web App (PWA)** technology, you can install the app directly onto your Android phone's home screen.

### Steps:
1. Double-click `start.bat` on your PC to start the PG API server.
2. Double-click `share_mobile.bat` to generate your Cloudflare Tunnel public URL (e.g., `https://random-words.trycloudflare.com`).
3. Open that URL on your Android phone using **Google Chrome**.
4. You will see an amber **"Install App"** button at the top header. Tap it!
   - *Alternatively, tap the 3 vertical dots (⋮) in the top-right corner of Chrome and select **"Install app"** or **"Add to Home screen"**.*
5. Tap **Install**.

### ✨ Features of the Installed PWA:
- App icon on your Android home screen and app drawer named **Latha PG**.
- Runs in **standalone full-screen** without browser address bars.
- Mobile bottom navigation bar for quick 1-thumb tab switching (**Overview**, **Rooms**, **Tenants**, **Billing**, **Mess**).
- Direct **WhatsApp** rent receipt sharing and one-tap **Phone Calling** to helpline numbers.
- Auto-updates whenever you restart or update the server!

---

## 📦 Method 2: 1-Click APK via PWABuilder (Cloud APK Generator)

If you strictly need a standalone `.apk` file to install or send via WhatsApp/Telegram:

1. Launch `share_mobile.bat` and copy the public HTTPS URL (e.g. `https://your-name.trycloudflare.com/dashboard/`).
2. Open [PWABuilder](https://www.pwabuilder.com/) on your browser.
3. Paste the URL and click **Start**.
4. PWABuilder will automatically validate the manifest and icons (already pre-configured!).
5. Click **"Package for Stores"** -> Choose **Android**.
6. Click **Generate** / **Download APK**.
7. Copy the `.apk` file to your phone, tap to install, and allow "Install from Unknown Sources" if prompted.

---

## ☁️ Method 3: Automated Cloud Build via GitHub Actions

We have included a pre-configured GitHub Actions workflow: [`.github/workflows/build-apk.yml`](file:///.github/workflows/build-apk.yml).

1. Push this repository to your GitHub account:
   ```bash
   git init
   git add .
   git commit -m "Add mobile app and APK build pipeline"
   git remote add origin https://github.com/YOUR_USERNAME/pg_management_api.git
   git push -u origin main
   ```
2. On GitHub, navigate to the **Actions** tab.
3. You will see the **Build Android APK** workflow running.
4. Once completed (~2 minutes), click on the workflow run.
5. Under **Artifacts**, download `LathaPGManager-Debug-APK.zip`.
6. Extract the zip to get `app-debug.apk` and transfer it to your phone!

---

## 🛠️ Method 4: Build Locally Using Android Studio

The complete native Android project is located in the [`android/`](file:///android/) directory.

1. Open **Android Studio**.
2. Select **Open** and choose the `android` folder located at:
   `c:\Users\MSMETC\.gemini\antigravity\scratch\pg_management_api\android`
3. Wait for Gradle to sync dependencies.
4. In Android Studio, click **Build** -> **Build Bundle(s) / APK(s)** -> **Build APK(s)**.
5. Once built, click **locate** to open the folder containing `app-debug.apk`.
6. Transfer `app-debug.apk` to your Android device and install it.

---

## ⚙️ Connecting the Android APK to your Server

When you open the installed Android APK:
1. Tap the **Settings (Gear icon)** in the top app bar.
2. Enter your backend URL:
   - **Cloudflare Tunnel URL** (from `share_mobile.bat`): e.g. `https://xxxx.trycloudflare.com` *(Works from anywhere on 4G/5G mobile data)*.
   - **Local WiFi IP**: e.g. `http://192.168.1.15:8000` *(When phone and PC share the same WiFi)*.
3. Tap **Save & Connect**. The app will immediately load the live PG management system!
