import os
from PIL import Image, ImageDraw

def generate_android_icons():
    src_icon = r"app/static/icon-512.png"
    src_maskable = r"app/static/icon-maskable-512.png"
    
    if not os.path.exists(src_icon):
        print(f"Source icon not found: {src_icon}")
        return

    img = Image.open(src_icon)
    maskable_img = Image.open(src_maskable) if os.path.exists(src_maskable) else img

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
        
        # 1. Standard Launcher Icon
        resized = img.resize((size, size), Image.Resampling.LANCZOS)
        out_file = os.path.join(folder_path, "ic_launcher.png")
        resized.save(out_file, "PNG")
        print(f"Generated {out_file} ({size}x{size})")

        # 2. Circular Round Launcher Icon (used on Android 7.1+ roundIcon)
        round_src = maskable_img.resize((size, size), Image.Resampling.LANCZOS).convert("RGBA")
        circle_mask = Image.new("L", (size, size), 0)
        draw = ImageDraw.Draw(circle_mask)
        draw.ellipse((0, 0, size, size), fill=255)
        
        round_icon = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        round_icon.paste(round_src, (0, 0), circle_mask)
        
        round_file = os.path.join(folder_path, "ic_launcher_round.png")
        round_icon.save(round_file, "PNG")
        print(f"Generated {round_file} ({size}x{size})")

if __name__ == "__main__":
    generate_android_icons()
