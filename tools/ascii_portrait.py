"""Render the GitHub avatar as the ASCII column used by the profile SVGs.

Run locally with the project venv; GitHub Actions never invokes this.

    .venv/bin/python tools/ascii_portrait.py            # preview as plain text
    .venv/bin/python tools/ascii_portrait.py --tspans   # emit SVG rows
"""
import argparse
import io
import pathlib
import urllib.request

from PIL import Image, ImageEnhance, ImageOps

AVATAR_URL = 'https://avatars.githubusercontent.com/u/57731496?v=4'
CACHE = pathlib.Path(__file__).parent / 'avatar.png'

COLS, ROWS = 40, 25
FIRST_ROW_Y, ROW_STEP = 90, 20      # centres 25 rows against the 30-row text column

# A 16px Consolas cell is ~9.6px wide against a 20px row, so the source crop has
# to be this much taller than wide to come out unsquashed.
CROP_ASPECT = (COLS * 9.6) / (ROWS * 20)

# Darkest ink first. The trailing spaces drop the flat backdrop to blank rather
# than a field of punctuation noise.
RAMP = "@$&M#WgqLc|;:,'.    "


def load_avatar():
    if not CACHE.exists():
        with urllib.request.urlopen(AVATAR_URL) as response:
            CACHE.write_bytes(response.read())
    return Image.open(io.BytesIO(CACHE.read_bytes())).convert('RGB')


def crop_portrait(image, zoom, x_bias, y_bias):
    width, height = image.size
    box_h = int(height * zoom)
    box_w = int(box_h * CROP_ASPECT)
    if box_w > width:
        box_w = width
        box_h = int(box_w / CROP_ASPECT)
    left = int((width - box_w) * x_bias)
    top = int((height - box_h) * y_bias)
    return image.crop((left, top, left + box_w, top + box_h))


def to_ascii(contrast, zoom, x_bias, y_bias, invert):
    grey = ImageOps.grayscale(crop_portrait(load_avatar(), zoom, x_bias, y_bias))
    grey = ImageEnhance.Contrast(grey).enhance(contrast)
    grey = ImageOps.autocontrast(grey, cutoff=2)
    grey = grey.resize((COLS, ROWS), Image.LANCZOS)
    if invert:
        grey = ImageOps.invert(grey)

    pixels = list(grey.getdata())
    scale = (len(RAMP) - 1) / 255
    rows = []
    for r in range(ROWS):
        row = pixels[r * COLS:(r + 1) * COLS]
        rows.append(''.join(RAMP[round(p * scale)] for p in row).rstrip())
    return rows


def escape(text):
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--contrast', type=float, default=4.2)
    parser.add_argument('--zoom', type=float, default=0.80)
    parser.add_argument('--x-bias', type=float, default=0.5)
    parser.add_argument('--y-bias', type=float, default=0.15)
    parser.add_argument('--invert', action='store_true')
    parser.add_argument('--tspans', action='store_true')
    args = parser.parse_args()

    rows = to_ascii(args.contrast, args.zoom, args.x_bias, args.y_bias, args.invert)
    for index, row in enumerate(rows):
        if args.tspans:
            y = FIRST_ROW_Y + index * ROW_STEP
            print(f'<tspan x="15" y="{y}">{escape(row)}</tspan>')
        else:
            print(f'|{row:<{COLS}}|')


if __name__ == '__main__':
    main()
