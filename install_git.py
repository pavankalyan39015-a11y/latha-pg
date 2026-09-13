import urllib.request
import json
import zipfile
import os
import shutil

def install_mingit():
    install_dir = os.path.expandvars(r"%LOCALAPPDATA%\Programs\MinGit")
    git_exe = os.path.join(install_dir, "cmd", "git.exe")
    if os.path.exists(git_exe):
        print("MinGit already exists at:", git_exe)
        return git_exe

    print("Fetching latest MinGit release from GitHub...")
    req = urllib.request.Request(
        "https://api.github.com/repos/git-for-windows/git/releases/latest",
        headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    # Find MinGit-*-64-bit.zip
    download_url = None
    for asset in data.get("assets", []):
        name = asset.get("name", "")
        if name.startswith("MinGit-") and name.endswith("-64-bit.zip") and "busybox" not in name:
            download_url = asset.get("browser_download_url")
            break

    if not download_url:
        # Fallback to any 64-bit MinGit
        for asset in data.get("assets", []):
            name = asset.get("name", "")
            if name.startswith("MinGit-") and "64-bit" in name:
                download_url = asset.get("browser_download_url")
                break

    if not download_url:
        print("MinGit download URL not found")
        return None

    print(f"Downloading {download_url}...")
    temp_zip = os.path.join(os.path.dirname(__file__), "mingit.zip")
    urllib.request.urlretrieve(download_url, temp_zip)
    print("Download complete. Extracting...")

    os.makedirs(install_dir, exist_ok=True)
    with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
        zip_ref.extractall(install_dir)

    os.remove(temp_zip)
    print("Extracted to:", install_dir)
    return git_exe

if __name__ == "__main__":
    exe = install_mingit()
    print("Git binary ready:", exe)
