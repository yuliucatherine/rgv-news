"""Cover image for a Short/Reel (1080x1920 JPEG): the hook in big type plus a frame from the Short's
footage, all kept inside the middle 4:5 band (y 285-1635) that Instagram and Facebook show in feeds and grids.
Usage: python3 pipeline/short_cover.py <short.json> <out.jpg> [frame_fraction=0.35]
Reads the clean 16:9 render that shorts_from_episode.py leaves in <out>_work/clean.mp4.
"""
import sys, os, json, subprocess, tempfile
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

W, H = 1080, 1920
FD = "/usr/share/fonts/opentype/inter"
NAVY = (9, 16, 32); ORANGE = (249, 115, 22); INK = (248, 250, 252); SUB = (203, 213, 225)
def F(w, s): return ImageFont.truetype(f"{FD}/Inter-{w}.otf", s)


def grab(video, frac):
    d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video]))
    tmp = tempfile.mktemp(suffix=".png")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{d * frac:.2f}", "-i", video, "-frames:v", "1", tmp], check=True)
    im = Image.open(tmp).convert("RGB"); os.remove(tmp); return im


def fit(text, maxw, size):
    while size > 40 and F("Black", size).getlength(text) > maxw: size -= 2
    return size


def main(cfg, out, frac=0.35):
    clean = os.path.splitext(cfg["out"])[0] + "_work/clean.mp4"
    fr = grab(clean, frac)
    # background: blurred, darkened footage under a navy wash
    bg = fr.resize((int(fr.width * H / fr.height), H)).crop((0, 0, W, H)) if fr.width * H / fr.height >= W else fr.resize((W, H))
    bg = ImageEnhance.Brightness(bg.filter(ImageFilter.GaussianBlur(40))).enhance(0.45)
    img = Image.blend(bg, Image.new("RGB", (W, H), NAVY), 0.55); d = ImageDraw.Draw(img)
    x0, y = 80, 360
    d.rectangle([x0, y, x0 + 230, y + 60], fill=ORANGE)
    d.text((x0 + 22, y + 10), "RGV NEWS", font=F("Black", 36), fill=NAVY)
    d.text((x0 + 252, y + 12), "INVESTOR BRIEF", font=F("Bold", 32), fill=SUB)
    y += 100
    for line in cfg["hook"]:
        orange = line.startswith("*") and line.endswith("*"); txt = line.strip("*")
        s = fit(txt, W - 2 * x0, 104)
        d.text((x0, y), txt, font=F("Black", s), fill=ORANGE if orange else INK, stroke_width=3, stroke_fill=NAVY)
        y += int(s * 1.1)
    y += 40
    pic = fr.resize((W, int(W * fr.height / fr.width)))
    img.paste(pic, (0, y)); d.rectangle([0, y - 4, W, y], fill=ORANGE); d.rectangle([0, y + pic.height, W, y + pic.height + 4], fill=ORANGE)
    yb = y + pic.height + 44
    if yb + 50 > 1630: raise SystemExit(f"cover too tall ({yb})")
    d.text((W // 2, yb), "Full breakdown on YouTube", font=F("Bold", 40), fill=INK, anchor="mt")
    img.save(out, quality=92); print("cover ok", out)


if __name__ == "__main__":
    main(json.load(open(sys.argv[1])), sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 0.35)
