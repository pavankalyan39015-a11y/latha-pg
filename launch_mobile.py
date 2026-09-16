import subprocess
import time
import re
import os
import sys
import qrcode
import io

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

def main():
    print("=" * 60)
    print("      LATHA PG MANAGER - MOBILE ACCESS LAUNCHER")
    print("=" * 60)
    print("1. Starting FastAPI Server (http://127.0.0.1:8000)...")

    # Start FastAPI server
    server_process = subprocess.Popen(
        [sys.executable, "run.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
    )

    time.sleep(2)
    print("   Server started successfully!")

    print("\n2. Starting Cloudflare Tunnel for secure public phone access...")
    tunnel_cmd = [os.path.abspath("cloudflared.exe"), "tunnel", "--url", "http://127.0.0.1:8000"]
    
    tunnel_process = subprocess.Popen(
        tunnel_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        encoding="utf-8",
        errors="replace"
    )

    public_url = None
    print("   Waiting for public link (takes 3-5 seconds)...")

    # Read output to capture https://*.trycloudflare.com
    for line in tunnel_process.stdout:
        match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
        if match:
            public_url = match.group(0)
            break

    if not public_url:
        print("   [!] Could not automatically capture Cloudflare URL.")
        print("   Using local Wi-Fi fallback: http://192.168.0.187:8000/dashboard/")
        public_url = "http://192.168.0.187:8000"

    dashboard_url = f"{public_url}/dashboard/"

    # Generate QR code image and HTML page for scanning
    try:
        qr_img = qrcode.make(dashboard_url)
        qr_img.save("mobile_qr.png")
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Latha PG Manager - Mobile Connect</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #031B40 0%, #062B63 100%); color: #f8fafc; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; margin: 0; padding: 20px; }}
        .card {{ background: rgba(11, 79, 156, 0.25); backdrop-filter: blur(12px); padding: 32px; border-radius: 20px; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.6); text-align: center; max-width: 440px; width: 100%; border: 1.5px solid rgba(255, 210, 0, 0.3); }}
        h1 {{ color: #FFD200; margin-top: 0; font-size: 22px; font-weight: 700; }}
        p {{ color: #D8E6F3; font-size: 14px; margin: 8px 0 20px; line-height: 1.5; }}
        .qr-wrapper {{ background: white; padding: 16px; border-radius: 16px; display: inline-block; margin-bottom: 20px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.3); border: 2px solid #FFD200; }}
        img {{ display: block; width: 220px; height: 220px; }}
        .url-box {{ background: #031B40; padding: 12px; border-radius: 10px; font-family: monospace; font-size: 13px; color: #FFD200; word-break: break-all; border: 1px solid #0B4F9C; margin-bottom: 16px; }}
        .badge {{ background: #10A875; color: white; padding: 5px 14px; border-radius: 9999px; font-size: 12px; font-weight: 700; display: inline-block; margin-bottom: 14px; letter-spacing: 0.5px; }}
        .instructions {{ text-align: left; background: #031B40; padding: 16px; border-radius: 10px; font-size: 13px; color: #EAF3FA; border-left: 4px solid #FFD200; }}
        .instructions ol {{ margin: 0; padding-left: 20px; }}
        .instructions li {{ margin-bottom: 6px; }}
    </style>
</head>
<body>
    <div class="card">
        <span class="badge">● Live &amp; Connected</span>
        <h1>📱 Open on Your Phone</h1>
        <p>Point your phone's camera at this QR code to instantly open Latha PG Manager:</p>
        
        <div class="qr-wrapper">
            <img src="mobile_qr.png" alt="Scan QR Code">
        </div>
        
        <div class="url-box">{dashboard_url}</div>
        
        <div class="instructions">
            <ol>
                <li>Scan the QR code with your phone camera or open the link above in Chrome.</li>
                <li>Tap <strong>"Install App"</strong> in the top bar to add it to your home screen!</li>
            </ol>
        </div>
    </div>
</body>
</html>"""
        with open("mobile_qr.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        
        import webbrowser
        webbrowser.open(os.path.abspath("mobile_qr.html"))
    except Exception as e:
        pass

    print("\n" + "=" * 60)
    print("       SUCCESS! SCAN QR CODE OR OPEN LINK ON PHONE")
    print("=" * 60)
    print(f"\n   Phone Link: {dashboard_url}\n")
    print("   Scan this QR code with your phone camera:")
    print("-" * 60)

    # Print ASCII QR code in terminal safely
    try:
        qr = qrcode.QRCode()
        qr.add_data(dashboard_url)
        qr.print_ascii(invert=True)
    except Exception:
        pass

    print("-" * 60)
    print(f"   URL: {dashboard_url}")
    print("\n   [How to use on phone]:")
    print("   1. Open link in Chrome on your phone.")
    print("   2. Tap 'Install App' or 'Add to Home Screen' for the full native experience!")
    print("\n   [Keep this window open while using the app on your phone]")
    print("   Press Ctrl+C to stop the server and tunnel.")
    print("=" * 60)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping mobile server and tunnel...")
        server_process.terminate()
        tunnel_process.terminate()
        print("Done.")

if __name__ == "__main__":
    main()
