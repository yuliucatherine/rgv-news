"""'Document' animation (1920x1080, 60 fps): a page of an official report slides in, tilted, the
camera drifts across it, and a highlighter sweeps over the key sentences one by one, each time
the view pulls in a little closer. Text is quoted verbatim from the source (credited on screen).
Usage: python3 pipeline/doc_highlight.py <config.json> <out.mp4>
config: {"seconds": 16, "fps": 60, "source": "2026 Rio Grande Regional Water Plan · Chapter 6",
         "heading": "6.3 Unmet Needs", "paragraphs": [{"text": "...", "highlight": [0.2, 0.45] or null}, ...]}
"""
import sys, os, json, shutil, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1920, 1080
FD = "/usr/share/fonts/opentype/inter"; SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIFB = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
NAVY = (9, 16, 32); PAPER = (247, 245, 240); TEXT = (25, 28, 36); HL = (253, 224, 71)
def F(w, s): return ImageFont.truetype(f"{FD}/Inter-{w}.otf", s)
def ease(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)


def wrap(d, text, font, maxw):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= maxw: cur = t
        else: lines.append(cur); cur = w
    return lines + [cur]


def main(cfg, out):
    fps = cfg.get("fps", 60); n = int(cfg.get("seconds", 14) * fps)
    PW, PH = 1500, 1900
    fb, fh, fs = ImageFont.truetype(SERIF, 40), ImageFont.truetype(SERIFB, 52), F("SemiBold", 26)
    page = Image.new("RGB", (PW, PH), PAPER); d = ImageDraw.Draw(page)
    d.text((110, 90), cfg.get("source", ""), font=fs, fill=(110, 116, 128))
    d.line([(110, 140), (PW - 110, 140)], fill=(200, 200, 200), width=2)
    d.text((110, 190), cfg.get("heading", ""), font=fh, fill=TEXT)
    y = 300; hl_boxes = []      # (paragraph index, [line boxes])
    for pi, p in enumerate(cfg["paragraphs"]):
        lines = wrap(d, p["text"], fb, PW - 220)
        boxes = []
        for ln in lines:
            d.text((110, y), ln, font=fb, fill=TEXT)
            boxes.append((110, y, 110 + d.textlength(ln, font=fb), y + 52)); y += 62
        if p.get("highlight") is not None: hl_boxes.append((p["highlight"], boxes))
        y += 40
    # dim filler lines below to read as a real page
    while y < PH - 120:
        for k in range(3):
            d.rectangle([110, y + 16, PW - 110 - (k * 170) % 500, y + 34], fill=(225, 223, 218)); y += 62
        y += 40
    shadow = Image.new("RGBA", (PW + 120, PH + 120), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rectangle([60, 70, PW + 60, PH + 70], fill=(0, 0, 0, 170))
    shadow = shadow.filter(ImageFilter.GaussianBlur(28))
    tmp = out + ".frames"; shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
    for f in range(n):
        t = f / max(1, n - 1)
        pg = page.copy(); dp = ImageDraw.Draw(pg, "RGBA")
        focus_y = 300
        for (h0, h1), boxes in hl_boxes:
            k = ease((t - h0) / max(1e-6, h1 - h0))
            if k <= 0: continue
            total = sum(b[2] - b[0] for b in boxes); done = total * k
            for (x0, y0, x1, y1) in boxes:
                w = min(x1 - x0, max(0, done)); done -= (x1 - x0)
                if w > 0: dp.rectangle([x0 - 6, y0 + 4, x0 + w + 6, y1 + 2], fill=HL + (150,))
            focus_y = boxes[0][1] if k < 1 else focus_y if focus_y != 300 else boxes[0][1]
            focus_y = boxes[0][1]
        # composite page onto background with tilt + slide-in + drift toward the active highlight
        a_in = ease(t / 0.12)
        scale = 0.62 + 0.18 * ease(t)
        pw, ph = int(PW * scale), int(PH * scale)
        im = pg.resize((pw, ph), Image.LANCZOS).convert("RGBA")
        sh = shadow.resize((int((PW + 120) * scale), int((PH + 120) * scale)))
        rot = -3.0 + 1.5 * ease(t)
        im = im.rotate(rot, resample=Image.BICUBIC, expand=True); sh = sh.rotate(rot, resample=Image.BICUBIC, expand=True)
        fr = Image.new("RGBA", (W, H), NAVY + (255,))
        gx = (W - im.width) // 2 + int(160 * (1 - a_in))
        gy = int(H * 0.42 - focus_y * scale) + int(60 * (1 - a_in))
        fr.alpha_composite(sh, (gx - int(60 * scale), gy - int(60 * scale)))
        fr.alpha_composite(im, (gx, gy))
        dd = ImageDraw.Draw(fr)
        dd.text((W - 40, H - 40), cfg.get("credit", "Source: " + cfg.get("source", "")), font=F("Medium", 22),
                fill=(203, 213, 225, 230), anchor="rs")
        fr.convert("RGB").save(f"{tmp}/{f:05d}.png")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", f"{tmp}/%05d.png",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", out], check=True)
    shutil.rmtree(tmp); print("doc ok", out)


if __name__ == "__main__":
    main(json.load(open(sys.argv[1])), sys.argv[2])
