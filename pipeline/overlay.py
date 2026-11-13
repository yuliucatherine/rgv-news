"""Reusable 2D overlays for RGV News shots (PIL): title scrim, tracked 3D labels, lower-third
callouts, data credits, and KINETIC EMPHASIS WORDS (big words popping in one by one on the left).
Usage as a script: python3 overlay.py <shot_overlay.json>
  config keys: frames_dir, out_mp4, fps_in, title, subtitle, credit, labels_json,
               callouts:[{text, sub, start, end}], kinetic:[{words:[...], start, step, hold}]
  (start/end/step/hold are fractions of the shot or seconds if "units":"s")
"""
import sys, os, json, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1920, 1080
FD = "/usr/share/fonts/opentype/inter"
NAVY = (9, 16, 32); INK = (241, 245, 249); SUB = (203, 213, 225); ORANGE = (249, 115, 22)


def F(w, s): return ImageFont.truetype(f"{FD}/Inter-{w}.otf", s)
def ease(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
def back(t):  # ease-out with a small overshoot for "pop"
    t = max(0.0, min(1.0, t)); c = 1.70158; return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2


def title(d, text, subtitle=None, a=1.0):
    for yy in range(0, 230, 2):
        d.rectangle([0, yy, W, yy + 2], fill=NAVY + (int(200 * a * (1 - yy / 230) ** 1.5),))
    d.rounded_rectangle([64, 60, 78, 112], 3, fill=ORANGE + (int(255 * a),))
    d.text((96, 58), text, font=F("Black", 44), fill=INK + (int(255 * a),))
    if subtitle:
        d.text((96, 112), subtitle, font=F("SemiBold", 30), fill=SUB + (int(255 * a),))


def credit(d, text):
    d.text((W - 40, H - 40), text, font=F("Medium", 22), fill=SUB + (220,), anchor="rs",
           stroke_width=3, stroke_fill=NAVY + (160,))


def tracked_labels(d, pts, a=1.0, avoid_left=0):
    for lab, (x, y, zc) in pts.items():
        if zc <= 0 or not (0.02 < x < 0.98 and 0.05 < y < 0.95): continue
        px, py = x * W, (1 - y) * H
        if px < avoid_left: continue
        d.line([(px, py), (px, py - 80)], fill=(255, 255, 255, int(220 * a)), width=3)
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=(255, 255, 255, int(255 * a)), outline=NAVY + (int(255 * a),), width=3)
        d.text((px, py - 88), lab, font=F("Bold", 32), fill=INK + (int(255 * a),), anchor="ms",
               stroke_width=5, stroke_fill=NAVY + (int(220 * a),))


def callout(d, text, sub, t):
    """Lower-third card sliding in from the left; t in [0,1] over its lifetime."""
    a = ease(min(t / 0.15, (1 - t) / 0.12, 1))
    if a <= 0: return
    x = -60 * (1 - a)
    f1, f2 = F("Black", 64), F("SemiBold", 30)
    w = max(d.textlength(text, font=f1), d.textlength(sub, font=f2)) + 90
    y = H - 330
    d.rounded_rectangle([64 + x, y, 64 + x + w, y + 150], 20, fill=NAVY + (int(225 * a),))
    d.rectangle([64 + x, y, 64 + x + 12, y + 150], fill=ORANGE + (int(255 * a),))
    d.text((106 + x, y + 18), text, font=f1, fill=INK + (int(255 * a),))
    d.text((106 + x, y + 98), sub, font=f2, fill=SUB + (int(255 * a),))


def kinetic(img, words, t_now, start, step, hold, fade=0.25):
    """Big emphasis words stacked on the left third, popping in one at a time.
    times in seconds. Returns the image with words composited (with a soft dark backing)."""
    end = start + step * len(words) + hold
    if t_now < start or t_now > end + fade: return img
    out_a = 1 - ease((t_now - end) / fade) if t_now > end else 1.0
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    size = 150 if len(words) <= 4 else 118
    f = F("Black", size); lh = int(size * 1.02)
    total_h = lh * len(words); y0 = (H - total_h) // 2 + 20
    # soft dark panel behind the words for legibility on any background
    panel = Image.new("L", (W, H), 0); pd = ImageDraw.Draw(panel)
    pd.rectangle([0, 0, int(W * 0.46), H], fill=int(170 * out_a))
    panel = panel.filter(ImageFilter.GaussianBlur(120))
    img = Image.composite(Image.new("RGB", (W, H), NAVY), img, panel)
    for i, wd in enumerate(words):
        ti = (t_now - start - i * step) / 0.28
        if ti <= 0: continue
        p = back(ti); a = ease(ti) * out_a
        x = 110 - int(50 * (1 - p)); y = y0 + i * lh
        col = ORANGE if wd.endswith("!") or wd.endswith("?") or wd.startswith("$") else INK
        d.text((x, y), wd, font=f, fill=col + (int(255 * a),))
    img = img.convert("RGBA"); img.alpha_composite(lay)
    return img.convert("RGB")


def run_config(cfg):
    fr = sorted(p for p in os.listdir(cfg["frames_dir"]) if p.startswith("f") and p.endswith(".png"))
    labels = json.load(open(cfg["labels_json"])) if cfg.get("labels_json") else {}
    fps = cfg.get("fps_in", 24); n = len(fr); dur = n / fps
    tmp = cfg["out_mp4"] + ".frames"; os.makedirs(tmp, exist_ok=True)
    for i, name in enumerate(fr):
        tn = i / fps; tr = i / max(1, n - 1)
        img = Image.open(os.path.join(cfg["frames_dir"], name)).convert("RGB").resize((W, H), Image.LANCZOS)
        for k in cfg.get("kinetic", []):
            img = kinetic(img, k["words"], tn, k["start"], k.get("step", 0.35), k.get("hold", 1.2))
        img = img.convert("RGBA"); d = ImageDraw.Draw(img, "RGBA")
        title(d, cfg.get("title", ""), cfg.get("subtitle"), ease(tr / 0.06))
        kin_on = any(k["start"] <= tn <= k["start"] + k.get("step", 0.35) * len(k["words"]) + k.get("hold", 1.2) + 0.25
                     for k in cfg.get("kinetic", []))
        la = ease((tr - cfg.get("labels_from", 0.0)) / 0.08)
        if la > 0 and str(i + 1) in labels:
            tracked_labels(d, labels[str(i + 1)], la, avoid_left=W * 0.47 if kin_on else 0)
        for c in cfg.get("callouts", []):
            s, e = c["start"], c["end"]
            if s <= tn <= e: callout(d, c["text"], c.get("sub", ""), (tn - s) / (e - s))
        if cfg.get("credit"): credit(d, cfg["credit"])
        img.convert("RGB").save(f"{tmp}/{i:04d}.png")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", f"{tmp}/%04d.png",
                    "-vf", "fps=30", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", cfg["out_mp4"]], check=True)
    print("overlay ok", cfg["out_mp4"], round(dur, 1), "s")


if __name__ == "__main__":
    run_config(json.load(open(sys.argv[1])))
