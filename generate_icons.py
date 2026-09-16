from PIL import Image, ImageDraw, ImageFont
import os

def create_pg_icon(size, output_path, maskable=False):
    """
    Generates high-resolution official brand icons for Latha PG Accommodation.
    Palette:
      - Deep Navy:  #062B63 -> (6, 43, 99)
      - Royal Blue: #0B4F9C -> (11, 79, 156)
      - Bright Gold:#FFD200 -> (255, 210, 0)
      - Pure White: #FFFFFF -> (255, 255, 255)
    """
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    navy_bg = (6, 43, 99, 255)
    gold_color = (255, 210, 0, 255)
    royal_blue = (11, 79, 156, 255)
    gold_glow = (255, 210, 0, 35)
    white_glow = (255, 255, 255, 230)

    # Scale factor for maskable safe-zone (Android adaptive circle crop uses inner 80%)
    scale = 0.82 if maskable else 0.96
    offset_y = int(size * 0.01)

    if maskable:
        # Full-bleed solid background for maskable
        draw.rectangle([(0, 0), (size, size)], fill=navy_bg)
    else:
        # Standard app icon with rounded squircle badge and golden border
        corner_radius = int(size * 0.22)
        border_width = max(3, int(size * 0.035))
        draw.rounded_rectangle(
            [(border_width // 2, border_width // 2), 
             (size - border_width // 2 - 1, size - border_width // 2 - 1)],
            radius=corner_radius,
            fill=navy_bg,
            outline=gold_color,
            width=border_width
        )

    # Inner subtle ambient golden glow circle
    glow_inset = int(size * (0.18 if maskable else 0.14))
    draw.ellipse(
        [(glow_inset, glow_inset + offset_y), (size - glow_inset, size - glow_inset + offset_y)],
        fill=gold_glow
    )

    # Building silhouette & structure
    tw = int(size * 0.44 * scale)
    th = int(size * 0.46 * scale)
    tx = (size - tw) // 2
    ty = int(size * (0.21 if maskable else 0.20))

    # Shadow under building
    draw.rectangle(
        [(tx + 4, ty + th - 2), (tx + tw - 4, ty + th + 4)],
        fill=(3, 20, 48, 120)
    )

    # Main Building Body (Royal Blue)
    draw.rounded_rectangle(
        [(tx, ty), (tx + tw, ty + th)],
        radius=max(3, int(size * 0.035)),
        fill=royal_blue,
        outline=gold_color,
        width=max(2, int(size * 0.015))
    )

    # Architectural Gable / Roof Peak (Gold with Navy trim)
    peak_y = ty - int(size * 0.10 * scale)
    draw.polygon([
        (tx + tw // 2, peak_y),
        (tx - int(size * 0.02 * scale), ty),
        (tx + tw + int(size * 0.02 * scale), ty)
    ], fill=gold_color)

    # Inner roof decorative medallion / star
    medallion_r = max(3, int(size * 0.025 * scale))
    mx = tx + tw // 2
    my = ty - int((ty - peak_y) * 0.42)
    draw.ellipse([(mx - medallion_r, my - medallion_r), (mx + medallion_r, my + medallion_r)], fill=navy_bg)

    # Illuminated Windows
    window_rows = 3
    window_cols = 3
    win_w = int(tw * 0.18)
    win_h = int(th * 0.15)
    spacing_x = int(tw * 0.10)
    spacing_y = int(th * 0.09)
    start_x = tx + int(tw * 0.12)
    start_y = ty + int(th * 0.15)

    for r in range(window_rows):
        for c in range(window_cols):
            wx = start_x + c * (win_w + spacing_x)
            wy = start_y + r * (win_h + spacing_y)
            # Alternating warm lighted windows
            is_lit = (r + c) % 2 == 0 or r == 0
            win_color = white_glow if is_lit else (255, 225, 90, 230)
            draw.rounded_rectangle(
                [(wx, wy), (wx + win_w, wy + win_h)],
                radius=max(2, int(size * 0.015)),
                fill=win_color
            )

    # Welcoming Archway Entrance Door
    door_w = int(tw * 0.30)
    door_h = int(th * 0.28)
    dx = tx + (tw - door_w) // 2
    dy = ty + th - door_h
    draw.rounded_rectangle(
        [(dx, dy), (dx + door_w, ty + th)],
        radius=max(3, int(size * 0.03)),
        fill=navy_bg,
        outline=gold_color,
        width=max(1, int(size * 0.01))
    )

    # Brand Text Banner at Bottom
    banner_w = int(size * (0.76 if maskable else 0.82))
    banner_h = int(size * 0.16 * scale)
    banner_x = (size - banner_w) // 2
    banner_y = int(size * (0.73 if maskable else 0.74))

    # Banner Shadow
    draw.rounded_rectangle(
        [(banner_x + 2, banner_y + 3), (banner_x + banner_w + 2, banner_y + banner_h + 3)],
        radius=int(banner_h * 0.35),
        fill=(0, 0, 0, 100)
    )

    # Banner Background (High-contrast Bright Gold)
    draw.rounded_rectangle(
        [(banner_x, banner_y), (banner_x + banner_w, banner_y + banner_h)],
        radius=int(banner_h * 0.35),
        fill=gold_color,
        outline=navy_bg,
        width=max(2, int(size * 0.012))
    )

    # Typography
    font_size = int(banner_h * 0.62)
    font = None
    windir = os.environ.get("WINDIR", r"C:\Windows")
    for fname in ["segoeuib.ttf", "arialbd.ttf", "calibrib.ttf"]:
        fpath = os.path.join(windir, "Fonts", fname)
        if os.path.exists(fpath):
            try:
                font = ImageFont.truetype(fpath, font_size)
                break
            except IOError:
                continue
    if not font:
        try:
            font = ImageFont.truetype("arialbd.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()

    text = "LATHA PG"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    text_x = (size - text_w) // 2
    text_y = banner_y + (banner_h - text_h) // 2 - int(size * 0.01)

    draw.text((text_x, text_y), text, fill=navy_bg, font=font)

    # Ensure output directory exists and save
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, "PNG")
    print(f"Generated {output_path} ({size}x{size}, maskable={maskable})")

if __name__ == "__main__":
    static_dir = os.path.abspath(r"app/static")
    create_pg_icon(192, os.path.join(static_dir, "icon-192.png"), maskable=False)
    create_pg_icon(512, os.path.join(static_dir, "icon-512.png"), maskable=False)
    create_pg_icon(512, os.path.join(static_dir, "icon-maskable-512.png"), maskable=True)
