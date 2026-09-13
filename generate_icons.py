from PIL import Image, ImageDraw, ImageFont
import os

def create_pg_icon(size, output_path):
    # Create image with amber gradient / background
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Rounded rectangle background
    corner_radius = int(size * 0.22)
    # Background color: slate-950 #020617 with amber border
    bg_color = (15, 23, 42, 255)       # Slate 900
    border_color = (245, 158, 11, 255) # Amber 500
    border_width = max(2, int(size * 0.03))

    # Outer border
    draw.rounded_rectangle(
        [(border_width // 2, border_width // 2), 
         (size - border_width // 2 - 1, size - border_width // 2 - 1)],
        radius=corner_radius,
        fill=bg_color,
        outline=border_color,
        width=border_width
    )

    # Inner decorative glow circle
    glow_color = (245, 158, 11, 40)
    glow_inset = int(size * 0.15)
    draw.ellipse(
        [(glow_inset, glow_inset), (size - glow_inset, size - glow_inset)],
        fill=glow_color
    )

    # Draw stylized building silhouette
    # Main tower
    tw = int(size * 0.44)
    th = int(size * 0.46)
    tx = (size - tw) // 2
    ty = int(size * 0.22)

    # Building body (amber-500)
    amber_color = (245, 158, 11, 255)
    amber_light = (252, 211, 77, 255)
    amber_dark = (217, 119, 6, 255)
    
    draw.rounded_rectangle(
        [(tx, ty), (tx + tw, ty + th)],
        radius=int(size * 0.04),
        fill=amber_color
    )

    # Roof peak / decorative top
    draw.polygon([
        (tx + tw // 2, int(size * 0.14)),
        (tx + int(tw * 0.1), ty),
        (tx + int(tw * 0.9), ty)
    ], fill=amber_light)

    # Building windows (slate 900)
    window_rows = 3
    window_cols = 3
    win_w = int(tw * 0.18)
    win_h = int(th * 0.16)
    spacing_x = int(tw * 0.10)
    spacing_y = int(th * 0.09)
    start_x = tx + int(tw * 0.12)
    start_y = ty + int(th * 0.15)

    for r in range(window_rows):
        for c in range(window_cols):
            wx = start_x + c * (win_w + spacing_x)
            wy = start_y + r * (win_h + spacing_y)
            # Yellow lighted windows vs dark windows
            win_fill = (255, 255, 255, 240) if (r + c) % 2 == 0 else (30, 41, 59, 255)
            draw.rounded_rectangle(
                [(wx, wy), (wx + win_w, wy + win_h)],
                radius=max(1, int(size * 0.015)),
                fill=win_fill
            )

    # Entrance door
    door_w = int(tw * 0.28)
    door_h = int(th * 0.25)
    dx = tx + (tw - door_w) // 2
    dy = ty + th - door_h
    draw.rounded_rectangle(
        [(dx, dy), (dx + door_w, ty + th)],
        radius=max(1, int(size * 0.02)),
        fill=(15, 23, 42, 255)
    )

    # "PG" Text Banner at bottom
    # Draw dark banner behind text
    banner_h = int(size * 0.18)
    banner_y = int(size * 0.74)
    draw.rounded_rectangle(
        [(int(size * 0.15), banner_y), (size - int(size * 0.15), banner_y + banner_h)],
        radius=int(banner_h * 0.35),
        fill=(245, 158, 11, 255)
    )

    # Try loading a bold font or draw clean text
    font_size = int(size * 0.12)
    try:
        font = ImageFont.truetype("arialbd.ttf", font_size)
    except IOError:
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()

    text = "LATHA PG"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    text_x = (size - text_w) // 2
    text_y = banner_y + (banner_h - text_h) // 2 - int(size * 0.01)

    draw.text((text_x, text_y), text, fill=(15, 23, 42, 255), font=font)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, "PNG")
    print(f"Generated {output_path} ({size}x{size})")

if __name__ == "__main__":
    static_dir = os.path.abspath(r"app/static")
    create_pg_icon(192, os.path.join(static_dir, "icon-192.png"))
    create_pg_icon(512, os.path.join(static_dir, "icon-512.png"))
    create_pg_icon(512, os.path.join(static_dir, "icon-maskable-512.png"))
