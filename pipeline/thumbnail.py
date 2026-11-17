"""YouTube thumbnail (1280x720 JPEG): full-bleed photo, navy gradient on the left, brand chip,
a big data number and a short headline. Rendered at 2x and downscaled for crisp edges.
Usage: python3 pipeline/thumbnail.py <config.json> <out.jpg>
config: {"photo": path, "crop": [x0,y0,x1,y1], "chip": "INVESTOR BRIEF", "kicker": "SPACEX'S",
         "number": "$986M", "headline": ["BET ON", "THE VALLEY"], "sub": "...", "tag": "STARBASE, TEXAS"}
"""
import sys, json
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import numpy as np

S = 2; W, H = 1280 * S, 720 * S
FD = "/usr/share/fonts/opentype/inter"
NAVY = (9, 16, 32); INK = (248, 250, 252); SUB = (203, 213, 225); ORANGE = (249, 115, 22)
def F(w, s): return ImageFont.truetype(f"{FD}/Inter-{w}.otf", s * S)


def main(cfg, out):
    src = Image.open(cfg["photo"]).convert("RGB")
    x0, y0, x1, y1 = cfg["crop"]
    if cfg.get("pad_color") and (x0 < 0 or y0 < 0 or x1 > src.width or y1 > src.height):   # flat padding (charts)
        cw, ch = x1 - x0, y1 - y0; canvas = Image.new("RGB", (cw, ch), tuple(cfg["pad_color"]))
        canvas.paste(src, (-x0, -y0)); src = canvas; x0, y0, x1, y1 = 0, 0, cw, ch
    if x0 < 0:   # crop reaches past the left edge: extend with a blurred stretch of the photo
        pad = -x0
        ext = Image.new("RGB", (src.width + pad, src.height))
        ext.paste(src.crop((0, 0, 40, src.height)).resize((pad, src.height)).filter(ImageFilter.GaussianBlur(30)), (0, 0))
        ext.paste(src, (pad, 0)); src = ext; x0 += pad; x1 += pad
    im = src.crop((x0, y0, x1, y1)).resize((W, H), Image.LANCZOS)
    im = ImageEnhance.Contrast(im).enhance(1.25); im = ImageEnhance.Color(im).enhance(1.15)
    # navy gradient from the left for the text column + a soft vignette at the bottom
    a = np.zeros((H, W), np.float32)
    x = np.linspace(0, 1, W)[None, :]; y = np.linspace(0, 1, H)[:, None]
    a = np.clip(1.0 - (x - 0.30) / 0.32, 0, 1) ** 1.3 * 0.94
    a = np.maximum(a, np.clip((y - 0.78) / 0.22, 0, 1) * 0.55)
    mask = Image.fromarray((a * 255).astype(np.uint8))
    im = Image.composite(Image.new("RGB", (W, H), NAVY), im, mask)
    d = ImageDraw.Draw(im)
    m = 56 * S
    # brand chip
    f = F("Black", 26); t1 = "RGV NEWS"; w1 = d.textlength(t1, font=f)
    d.rectangle([m, m, m + w1 + 36 * S, m + 52 * S], fill=ORANGE)
    d.text((m + 18 * S, m + 26 * S), t1, font=f, fill=NAVY, anchor="lm")
    f2 = F("Bold", 24)
    d.text((m + w1 + 54 * S, m + 26 * S), cfg["chip"], font=f2, fill=INK, anchor="lm")
    yy = m + 100 * S
    d.text((m - 4 * S, yy), cfg["kicker"], font=F("Black", 78), fill=INK)
    yy += 84 * S
    d.text((m - 8 * S, yy), cfg["number"], font=F("Black", 176), fill=ORANGE)
    yy += 186 * S
    for line in cfg["headline"]:
        d.text((m - 4 * S, yy), line, font=F("Black", 74), fill=INK); yy += 80 * S
    d.rectangle([m, yy + 18 * S, m + 90 * S, yy + 26 * S], fill=ORANGE)
    d.text((m, yy + 44 * S), cfg["sub"], font=F("SemiBold", 28), fill=SUB)
    if cfg.get("tag"):
        ft = F("Bold", 24); tw = d.textlength(cfg["tag"], font=ft)
        x1, y1 = W - m, H - m
        d.rounded_rectangle([x1 - tw - 64 * S, y1 - 46 * S, x1, y1], 8 * S, fill=NAVY + (0,))
        d.ellipse([x1 - tw - 46 * S, y1 - 30 * S, x1 - tw - 32 * S, y1 - 16 * S], fill=ORANGE)
        d.text((x1 - tw - 20 * S, y1 - 23 * S), cfg["tag"], font=ft, fill=INK, anchor="lm",
               stroke_width=3 * S, stroke_fill=NAVY)
    im.resize((1280, 720), Image.LANCZOS).save(out, quality=92, optimize=True)
    print("thumbnail ok", out)


if __name__ == "__main__":
    main(json.load(open(sys.argv[1])), sys.argv[2])
