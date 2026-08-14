"""
Build-time asset generator for the tool-card icon badges.

Draws a small set of flat, white line-glyphs on a rounded-square accent
gradient badge (matching the main app icon's visual language) purely with
Pillow, and saves them as transparent PNGs.

Run manually whenever the icon design changes:
    venv\\Scripts\\python assets\\icons\\generate_tool_icons.py
"""

import os

from PIL import Image, ImageDraw

SIZE = 256
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools")

ACCENT_START = (79, 70, 229)   # indigo #4f46e5
ACCENT_END = (99, 102, 241)    # indigo #6366f1
WHITE = (255, 255, 255, 255)


def build_badge():
    gradient = Image.linear_gradient("L").resize((SIZE * 2, SIZE * 2))
    gradient = gradient.rotate(45, expand=False)
    left = (gradient.width - SIZE) // 2
    top = (gradient.height - SIZE) // 2
    gradient = gradient.crop((left, top, left + SIZE, top + SIZE))

    color_a = Image.new("RGBA", (SIZE, SIZE), ACCENT_START)
    color_b = Image.new("RGBA", (SIZE, SIZE), ACCENT_END)
    blended = Image.composite(color_b, color_a, gradient)

    mask = Image.new("L", (SIZE, SIZE), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, SIZE - 1, SIZE - 1], radius=56, fill=255)

    badge = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    badge.paste(blended, (0, 0), mask)
    return badge


def draw_resize(canvas):
    draw = ImageDraw.Draw(canvas)
    c = SIZE / 2
    arm = 34
    gap = 30
    width = 16

    # Four corner brackets pointing outward from a central square (expand icon)
    for sx, sy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
        ox, oy = c + sx * gap, c + sy * gap
        draw.line([(ox, oy), (ox + sx * arm, oy)], fill=WHITE, width=width)
        draw.line([(ox, oy), (ox, oy + sy * arm)], fill=WHITE, width=width)
        r = width / 2
        draw.ellipse([ox - r, oy - r, ox + r, oy + r], fill=WHITE)
        draw.ellipse(
            [ox + sx * arm - r, oy - r, ox + sx * arm + r, oy + r], fill=WHITE
        )
        draw.ellipse(
            [ox - r, oy + sy * arm - r, ox + r, oy + sy * arm + r], fill=WHITE
        )


def draw_image(canvas):
    draw = ImageDraw.Draw(canvas)
    frame = [58, 70, SIZE - 58, SIZE - 70]
    fw = frame[2] - frame[0]
    fh = frame[3] - frame[1]

    draw.rounded_rectangle(frame, radius=14, outline=WHITE, width=12)

    sun_cx = frame[0] + fw * 0.28
    sun_cy = frame[1] + fh * 0.32
    sun_r = 14
    draw.ellipse(
        [sun_cx - sun_r, sun_cy - sun_r, sun_cx + sun_r, sun_cy + sun_r], fill=WHITE
    )

    base_y = frame[3] - fh * 0.16
    peak1_y = frame[1] + fh * 0.42
    peak2_y = frame[1] + fh * 0.56

    draw.polygon(
        [
            (frame[0] + fw * 0.12, base_y),
            (frame[0] + fw * 0.42, peak1_y),
            (frame[0] + fw * 0.66, base_y),
        ],
        fill=WHITE,
    )
    draw.polygon(
        [
            (frame[0] + fw * 0.52, base_y),
            (frame[0] + fw * 0.76, peak2_y),
            (frame[0] + fw * 0.90, base_y),
        ],
        fill=WHITE,
    )


def draw_document(canvas):
    draw = ImageDraw.Draw(canvas)
    doc = [78, 52, SIZE - 78, SIZE - 52]
    fold = 34

    draw.polygon(
        [
            (doc[0], doc[1]),
            (doc[2] - fold, doc[1]),
            (doc[2], doc[1] + fold),
            (doc[2], doc[3]),
            (doc[0], doc[3]),
        ],
        fill=WHITE,
    )
    draw.polygon(
        [(doc[2] - fold, doc[1]), (doc[2], doc[1] + fold), (doc[2] - fold, doc[1] + fold)],
        fill=ACCENT_START,
    )

    line_x0 = doc[0] + 26
    line_x1 = doc[2] - 30
    line_x1_short = line_x0 + (line_x1 - line_x0) * 0.55
    for i, y in enumerate([doc[1] + 70, doc[1] + 100, doc[1] + 130]):
        x1 = line_x1 if i != 2 else line_x1_short
        draw.rounded_rectangle([line_x0, y, x1, y + 12], radius=6, fill=ACCENT_START)


def draw_lock(canvas, locked=True):
    draw = ImageDraw.Draw(canvas)
    cx, cy = SIZE / 2, SIZE / 2 + 12

    body = [cx - 52, cy - 4, cx + 52, cy + 78]
    draw.rounded_rectangle(body, radius=18, fill=WHITE)

    if locked:
        shackle_bbox = [cx - 34, cy - 82, cx + 34, cy + 10]
        draw.arc(shackle_bbox, start=180, end=360, fill=WHITE, width=20)
    else:
        shackle_bbox_open = [cx - 4, cy - 82, cx + 64, cy + 10]
        draw.arc(shackle_bbox_open, start=180, end=360, fill=WHITE, width=20)

    keyhole_cx, keyhole_cy = cx, cy + 32
    draw.ellipse(
        [keyhole_cx - 10, keyhole_cy - 12, keyhole_cx + 10, keyhole_cy + 8],
        fill=ACCENT_START,
    )
    draw.polygon(
        [
            (keyhole_cx - 6, keyhole_cy + 2),
            (keyhole_cx + 6, keyhole_cy + 2),
            (keyhole_cx + 10, keyhole_cy + 26),
            (keyhole_cx - 10, keyhole_cy + 26),
        ],
        fill=ACCENT_START,
    )


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    icons = {
        "resize": draw_resize,
        "image": draw_image,
        "document": draw_document,
        "lock": lambda c: draw_lock(c, locked=True),
        "unlock": lambda c: draw_lock(c, locked=False),
    }

    for name, drawer in icons.items():
        canvas = build_badge()
        drawer(canvas)
        out_path = os.path.join(OUT_DIR, f"{name}.png")
        canvas.save(out_path, "PNG")
        print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
