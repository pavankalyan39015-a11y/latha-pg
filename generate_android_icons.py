import os
from PIL import Image

def generate_android_icons():
    src_icon = r"app/static/icon-512.png"
    if not os.path.exists(src_icon):
        print("Source icon not found")
        return
    
    img = Image.open(src_icon)

    mipmap_sizes = {
        "mipmap-mdpi": 48,
        "mipmap-hdpi": 72,
        "mipmap-xhdpi": 96,
        "mipmap-xxhdpi": 144,
        "mipmap-xxxhdpi": 192,
    }

    base_res = r"android/app/src/main/res"
    for folder, size in mipmap_sizes.items():
        folder_path = os.path.join(base_res, folder)
        os.makedirs(folder_path, exist_ok=True)
        resized = img.resize((size, size), Image.Resampling.LANCZOS)
        out_file = os.path.join(folder_path, "ic_launcher.png")
        resized.save(out_file, "PNG")
        print(f"Generated {out_file} ({size}x{size})")

if __name__ == "__main__":
    generate_android_icons()
