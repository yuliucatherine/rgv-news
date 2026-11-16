"""'On the record' montage: real headlines from the outlets an episode cites, as our own animated
cards (outlet name, exact headline, date; no logos, no broadcast footage, so no Content ID risk).
Cards slide in one at a time over a slow push-in, then 'Full sources in the description'.
Usage: python3 pipeline/headlines.py <headlines.json> <out.mp4>
config: {"fps": 60, "seconds": 8.5, "title": "ON THE RECORD", "subtitle": "...",
         "items": [{"outlet": "KRGV", "date": "Aug 28, 2026", "headline": "..."}, ...]}
"""
import sys, os, json, math, subprocess, shutil
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1920, 1080
FD = "/usr/share/fonts/opentype/inter"; SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
NAVY = (9, 16, 32); INK = (241, 245, 249); SUB = (148, 163, 184); ORANGE = (249, 115, 22)
PAPER = (247, 245, 240); TEXT = (20, 24, 33); GREY = (100, 108, 120)
def F(w, s): return ImageFont.truetype(f"{FD}/Inter-{w}.otf", s)
def ease(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
def back(t):
    t = max(0.0, min(1.0, t)); c = 1.4; return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2


def wrap(d, text, font, maxw):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= maxw: cur = t
        else: lines.append(cur); cur = w
    return lines + [cur]


def card(item, cw=820):
    fh = ImageFont.truetype(SERIF, 40); fo = F("Black", 22); fdt = F("Medium", 22)
    tmp = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    lines = wrap(tmp, f"“{item['headline']}”", fh, cw - 80)
    ch = 92 + 48 * len(lines) + 24
    im = Image.new("RGBA", (cw + 40, ch + 40), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle([24, 28, cw + 24, ch + 28], 10, fill=(0, 0, 0, 150))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([20, 20, cw + 20, ch + 20], 10, fill=PAPER)
    d.rectangle([20, 20, 30, ch + 20], fill=ORANGE)
    d.text((58, 46), item["outlet"].upper(), font=fo, fill=ORANGE)
    d.text((cw - 10, 46), item["date"], font=fdt, fill=GREY, anchor="ra")
    y = 92
    for ln in lines:
        d.text((58, y), ln, font=fh, fill=TEXT); y += 48
    return im


def main(cfg, out):
    fps = cfg.get("fps", 60); secs = cfg.get("seconds", 8.5); n = int(fps * secs)
    items = cfg["items"]
    cards = [card(it).rotate(r, resample=Image.BICUBIC, expand=True)
             for it, r in zip(items, [-1.6, 1.2, -0.8, 1.5, -1.2, 0.9, -1.0, 1.3])]
    # cascading 2-column layout
    slots = []
    for i, c in enumerate(cards):
        col, row = i % 2, i // 2
        slots.append((90 + col * 900 + (row % 2) * 30, 230 + row * 255 - (col * 22)))
    bg = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(bg)
    for x in range(0, W, 80): d.line([(x, 0), (x, H)], fill=(18, 28, 50), width=1)
    for y in range(0, H, 80): d.line([(0, y), (W, y)], fill=(18, 28, 50), width=1)
    start, step = 0.35, cfg.get("step", 0.75)
    tmp = out + ".frames"; shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
    for f in range(n):
        t = f / fps
        fr = bg.copy().convert("RGBA")
        for i, (c, (x, y)) in enumerate(zip(cards, slots)):
            p = (t - start - i * step) / 0.5
            if p <= 0: continue
            a = ease(p); dy = int(70 * (1 - back(p)))
            layer = c.copy(); layer.putalpha(layer.getchannel("A").point(lambda v: int(v * a)))
            fr.alpha_composite(layer, (x, y + dy))
        # slow push-in on the whole board
        z = 1 + 0.05 * ease(t / secs)
        zw, zh = int(W * z), int(H * z)
        fr = fr.resize((zw, zh), Image.BICUBIC).crop(((zw - W) // 2, (zh - H) // 2, (zw - W) // 2 + W, (zh - H) // 2 + H))
        dd = ImageDraw.Draw(fr)
        ta = ease(t / 0.4)
        for yy in range(0, 200, 2):
            dd.rectangle([0, yy, W, yy + 2], fill=NAVY + (int(230 * (1 - yy / 200) ** 1.4),))
        dd.rounded_rectangle([64, 60, 78, 112], 3, fill=ORANGE + (int(255 * ta),))
        dd.text((96, 58), cfg.get("title", "ON THE RECORD"), font=F("Black", 50), fill=INK + (int(255 * ta),))
        dd.text((96, 120), cfg.get("subtitle", ""), font=F("SemiBold", 30), fill=SUB + (int(255 * ta),))
        ea = ease((t - (start + step * len(cards) + 0.4)) / 0.5)
        if ea > 0:
            msg = cfg.get("footer", "Full sources linked in the description")
            fw = dd.textlength(msg, font=F("Bold", 34))
            dd.rounded_rectangle([(W - fw) / 2 - 30, H - 120, (W + fw) / 2 + 30, H - 56], 12, fill=NAVY + (int(235 * ea),))
            dd.text((W / 2, H - 88), msg, font=F("Bold", 34), fill=INK + (int(255 * ea),), anchor="mm")
        fr.convert("RGB").save(f"{tmp}/{f:05d}.png")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", f"{tmp}/%05d.png",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", out], check=True)
    shutil.rmtree(tmp)
    print("headlines ok", out)


if __name__ == "__main__":
    main(json.load(open(sys.argv[1])), sys.argv[2])
