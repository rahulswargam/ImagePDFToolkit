"""
Build-time asset generator.

Draws the app icon (a folded document with an image glyph, on an indigo
-> violet gradient rounded-square background) purely with Pillow and saves
it as both a multi-resolution .ico (for the window/taskbar/exe/installer)
and a .png (for in-app use).

Run manually whenever the icon design changes:
    venv\\Scripts\\python assets\\icons\\generate_icon.py
"""

import os

from PIL import Image, ImageDraw

SIZE = 1024
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

ACCENT_START = (79, 70, 229)   # indigo #4f46e5
ACCENT_END = (99, 102, 241)    # indigo #6366f1
WHITE = (255, 255, 255, 255)
FOLD_SHADE = (224, 224, 250, 255)
GLYPH_LIGHT = (238, 242, 255, 255)
GLYPH_SUN = (250, 204, 21, 255)     # amber
GLYPH_MOUNTAIN = (79, 70, 229, 255)


def rounded_mask(size, radius):
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=255)
    return mask


def build_background():
    gradient = Image.linear_gradient("L").resize((SIZE * 2, SIZE * 2))
    gradient = gradient.rotate(45, expand=False)
    left = (gradient.width - SIZE) // 2
    top = (gradient.height - SIZE) // 2
    gradient = gradient.crop((left, top, left + SIZE, top + SIZE))

    color_a = Image.new("RGBA", (SIZE, SIZE), ACCENT_START)
    color_b = Image.new("RGBA", (SIZE, SIZE), ACCENT_END)
    blended = Image.composite(color_b, color_a, gradient)

    mask = rounded_mask(SIZE, radius=210)
    background = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    background.paste(blended, (0, 0), mask)
    return background


def draw_document(canvas):
    draw = ImageDraw.Draw(canvas)

    doc_w, doc_h = 520, 660
    doc_x = (SIZE - doc_w) // 2 + 50
    doc_y = (SIZE - doc_h) // 2 - 10
    fold = 100

    draw.rounded_rectangle(
        [doc_x, doc_y, doc_x + doc_w, doc_y + doc_h],
        radius=36,
        fill=WHITE,
    )

    draw.polygon(
        [
            (doc_x + doc_w - fold, doc_y),
            (doc_x + doc_w, doc_y + fold),
            (doc_x + doc_w - fold, doc_y + fold),
        ],
        fill=FOLD_SHADE,
    )

    # Text lines near the top of the document
    line_x0 = doc_x + 70
    line_x1 = doc_x + doc_w - fold - 30
    for i, line_y in enumerate([doc_y + 90, doc_y + 130]):
        x1 = line_x1 if i == 0 else line_x1 - 90
        draw.rounded_rectangle([line_x0, line_y, x1, line_y + 22], radius=11, fill=GLYPH_LIGHT)

    # Image placeholder frame
    frame_x0 = doc_x + 60
    frame_y0 = doc_y + 210
    frame_x1 = doc_x + doc_w - 60
    frame_y1 = doc_y + doc_h - 70
    draw.rounded_rectangle([frame_x0, frame_y0, frame_x1, frame_y1], radius=24, fill=GLYPH_LIGHT)

    # Sun
    sun_r = 34
    sun_cx = frame_x0 + 100
    sun_cy = frame_y0 + 90
    draw.ellipse(
        [sun_cx - sun_r, sun_cy - sun_r, sun_cx + sun_r, sun_cy + sun_r],
        fill=GLYPH_SUN,
    )

    # Mountains
    base_y = frame_y1 - 40
    draw.polygon(
        [
            (frame_x0 + 20, base_y),
            (frame_x0 + 160, frame_y0 + 120),
            (frame_x0 + 260, base_y),
        ],
        fill=GLYPH_MOUNTAIN,
    )
    draw.polygon(
        [
            (frame_x0 + 190, base_y),
            (frame_x0 + 300, frame_y0 + 150),
            (frame_x1 - 30, base_y),
        ],
        fill=ACCENT_END,
    )


def main():
    canvas = build_background()
    draw_document(canvas)

    png_path = os.path.join(OUT_DIR, "app.png")
    canvas.save(png_path, "PNG")

    ico_path = os.path.join(OUT_DIR, "app.ico")
    canvas.save(
        ico_path,
        sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )

    print(f"Saved {png_path}")
    print(f"Saved {ico_path}")


if __name__ == "__main__":
    main()
