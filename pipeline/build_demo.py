"""Assemble the 30-second RGV News visual demo.
Shots: 1 animated map (map_anim.py), 2 Blender terrain (terrain_shot.py), 3 animated funding
chart, 4 NASA photo pan + end card. Narration: free local voice (demo only).
Usage: python3 build_demo.py <repo_dir>
"""
import sys, os, json, math, subprocess
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFont, ImageFilter

R = sys.argv[1]; D = f"{R}/demo"; os.makedirs(D, exist_ok=True)
W, H, FPS = 1920, 1080, 30
FD = "/usr/share/fonts/opentype/inter"
NAVY = (9, 16, 32); INK = (241, 245, 249); MUTED = (148, 163, 184); ORANGE = (249, 115, 22)
BLUE = (56, 189, 248); TEAL = (52, 211, 153)


def F(w, s): return ImageFont.truetype(f"{FD}/Inter-{w}.otf", s)
def ease(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
def run(*a): subprocess.run(list(a), check=True)
def dur(p): return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]))


# ---------- narration (free local voice; the real episodes use ElevenLabs James) ----------
LINES = [
    "The Rio Grande Valley runs on one river. Four counties, about one point four million people, and nearly all of their water depends on the Rio Grande.",
    "Upstream, Falcon Reservoir is the Valley's savings account. In drought, it drains.",
    "Now, a hundred and sixty-four million dollar plan aims to stop losing water in old, leaky canals.",
    "For builders and investors, the question is simple. Where will the water be? This is R G V News.",
]
from kokoro_onnx import Kokoro
k = Kokoro(f"{R}/models/kokoro-v1.0.onnx", f"{R}/models/voices-v1.0.bin")
segs = []
for i, t in enumerate(LINES):
    s, sr = k.create(t, voice="am_michael", speed=1.08, lang="en-us")
    sf.write(f"{D}/vo{i}.wav", s, sr); segs.append(len(s) / sr)
print("narration secs", [round(x, 1) for x in segs])

# ---------- shot 2 overlay: labels + credits on the Blender frames ----------
fr = sorted(p for p in os.listdir(f"{D}/shot2_frames") if p.startswith("f") and p.endswith(".png"))
labels = json.load(open(f"{D}/shot2_frames/labels.json"))
o2 = f"{D}/shot2_over"; os.makedirs(o2, exist_ok=True)
for n, name in enumerate(fr):
    im = Image.open(f"{D}/shot2_frames/{name}").convert("RGB").resize((W, H), Image.LANCZOS)
    d = ImageDraw.Draw(im, "RGBA"); t = n / max(1, len(fr) - 1)
    for yy in range(0, 230, 2):
        d.rectangle([0, yy, W, yy + 2], fill=NAVY + (int(200 * (1 - yy / 230) ** 1.5),))
    d.rounded_rectangle([64, 60, 78, 112], 3, fill=ORANGE)
    d.text((96, 58), "FALCON INTERNATIONAL RESERVOIR", font=F("Black", 44), fill=INK)
    d.text((96, 112), "Starr & Zapata counties, Texas · Tamaulipas, Mexico", font=F("SemiBold", 30), fill=(203, 213, 225))
    for lab, (x, y, zc) in labels[str(n + 1)].items():
        if zc <= 0 or not (0 < x < 1 and 0 < y < 1): continue
        px, py = x * W, (1 - y) * H
        d.line([(px, py), (px, py - 70)], fill=(255, 255, 255, 220), width=3)
        d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=(255, 255, 255, 255))
        d.text((px, py - 78), lab, font=F("Bold", 32), fill=INK, anchor="ms", stroke_width=4, stroke_fill=NAVY)
    a = ease((t - 0.25) / 0.15)
    if a > 0:
        d.rounded_rectangle([64, 160, 64 + 470, 160 + 54], 27, fill=(251, 191, 36, int(235 * a)))
        d.text((88, 172), "ILLUSTRATIVE DRAWDOWN", font=F("Black", 28), fill=NAVY + (int(255 * a),))
    d.text((W - 40, H - 40), "3D terrain: AWS Terrain Tiles (SRTM / USGS 3DEP) · Water level illustrative",
           font=F("Medium", 22), fill=(203, 213, 225, 220), anchor="rs")
    im.save(f"{o2}/{n:04d}.png")
run("ffmpeg", "-y", "-loglevel", "error", "-framerate", "24", "-i", f"{o2}/%04d.png",
    "-vf", "fps=30", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", f"{D}/shot2_terrain.mp4")

# ---------- shot 3: animated funding chart ----------
def chart(out, secs):
    o = f"{D}/shot3_frames"; os.makedirs(o, exist_ok=True)
    n = int(secs * FPS)
    rows = [("Up to $76M", 76, "NADBank Water Resiliency Fund financing", BLUE),
            ("~$70M", 70, "Texas Water Development Board grants", TEAL)]
    for i in range(n):
        t = i / (n - 1)
        im = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(im, "RGBA")
        d.ellipse([W - 700, -500, W + 500, 500], fill=(56, 189, 248, 18))
        a0 = ease(t / 0.12)
        d.text((120, 120), "PROPOSED · SUBJECT TO BOARD APPROVALS", font=F("Bold", 32), fill=(52, 211, 153, int(255 * a0)))
        total = int(164 * ease(t / 0.55))
        d.text((120, 170), f"${total}M", font=F("Black", 200), fill=INK + (int(255 * a0),))
        d.text((120 + d.textlength(f"${total}M", font=F("Black", 200)) + 30, 300), "to modernize Valley canals",
               font=F("Bold", 52), fill=(203, 213, 225, int(255 * a0)))
        y = 520
        for j, (lab, v, desc, col) in enumerate(rows):
            g = ease((t - 0.12 - j * 0.12) / 0.45)
            bw = int(1300 * v / 80 * g)
            d.rounded_rectangle([120, y, 120 + max(bw, 1), y + 90], 18, fill=col + (230,))
            d.text((150, y + 18), lab, font=F("Black", 50), fill=NAVY if bw > 360 else INK)
            d.text((120, y + 105), desc, font=F("SemiBold", 34), fill=(203, 213, 225, int(255 * g)))
            y += 210
        g = ease((t - 0.62) / 0.2)
        if g > 0:
            d.rounded_rectangle([1150, 880, 1800, 990], 24, fill=(20, 32, 56, int(240 * g)), outline=(51, 65, 85), width=3)
            d.text((1180, 900), f"~{int(44000 * g):,} acre-feet", font=F("Black", 44), fill=INK + (int(255 * g),))
            d.text((1180, 952), "estimated water saved per year", font=F("Medium", 28), fill=(203, 213, 225, int(255 * g)))
        d.text((W - 40, H - 40), "Sources: NADBank (2026); Dallas Express. Figures as announced, pending approvals.",
               font=F("Medium", 22), fill=(203, 213, 225, 220), anchor="rs")
        im.save(f"{o}/{i:04d}.png")
    run("ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{o}/%04d.png",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", out)


# ---------- shot 4: NASA image vertical pan + end card ----------
def photo(out, secs, card_secs=2.2):
    o = f"{D}/shot4_frames"; os.makedirs(o, exist_ok=True)
    src = Image.open(f"{R}/data/imagery/PIA25446.jpg").convert("RGB")
    sw = src.width; scale = W / sw; big = src.resize((W, int(src.height * scale)), Image.LANCZOS)
    n = int(secs * FPS); nc = int(card_secs * FPS)
    for i in range(n + nc):
        if i < n:
            t = ease(i / (n - 1))
            # pan from the upper reservoir down toward the dam, slight push-in
            z = 1.0 + 0.06 * t
            cw, ch = W / z, H / z
            y0 = (big.height - ch) * (0.30 + 0.45 * t); x0 = (W - cw) / 2
            im = big.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.LANCZOS)
            d = ImageDraw.Draw(im, "RGBA")
            d.rectangle([0, H - 150, W, H], fill=NAVY + (200,))
            d.rectangle([0, H - 150, 10, H], fill=ORANGE)
            d.text((60, H - 132), "Falcon International Reservoir from orbit (false color: vegetation shows red)",
                   font=F("Bold", 34), fill=INK)
            d.text((60, H - 80), "Image: NASA/METI/AIST/Japan Space Systems, and U.S./Japan ASTER Science Team",
                   font=F("Medium", 26), fill=(203, 213, 225))
            if i > n - 12:  # fade to navy into the card
                im = Image.blend(im, Image.new("RGB", (W, H), NAVY), (i - (n - 12)) / 12)
        else:
            t = ease((i - n) / 10)
            im = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(im, "RGBA")
            d.rounded_rectangle([W // 2 - 260, H // 2 - 70, W // 2 - 240, H // 2 + 10], 4, fill=ORANGE + (int(255 * t),))
            d.text((W // 2 - 215, H // 2 - 74), "RGV NEWS", font=F("Black", 96), fill=INK + (int(255 * t),))
            d.text((W // 2, H // 2 + 60), "Texas development, explained for builders & investors",
                   font=F("SemiBold", 36), fill=(203, 213, 225, int(255 * t)), anchor="ma")
        im.save(f"{o}/{i:04d}.png")
    run("ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{o}/%04d.png",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", out)


GAP = 0.25
s1, s2 = dur(f"{D}/shot1_map.mp4"), dur(f"{D}/shot2_terrain.mp4")
chart(f"{D}/shot3_chart.mp4", segs[2] + 1.2)
photo(f"{D}/shot4_photo.mp4", max(4.5, segs[3] - 1.2), 2.4)
shots = [f"{D}/shot1_map.mp4", f"{D}/shot2_terrain.mp4", f"{D}/shot3_chart.mp4", f"{D}/shot4_photo.mp4"]
starts, t = [], 0.0
for sh in shots: starts.append(t); t += dur(sh)
total = t
# picture: concat; sound: each line starts with its shot (line 0 a beat in)
lst = f"{D}/concat.txt"
open(lst, "w").write("".join(f"file '{s}'\n" for s in shots))
run("ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", f"{D}/picture.mp4")
delays = [0.4, starts[1] + 0.2, starts[2] + 0.2, starts[3] + 0.3]
inputs = []; flt = []
for i, dl in enumerate(delays):
    inputs += ["-i", f"{D}/vo{i}.wav"]
    flt.append(f"[{i+1}:a]adelay={int(dl*1000)}|{int(dl*1000)},aresample=48000[a{i}]")
mix = ";".join(flt) + ";" + "".join(f"[a{i}]" for i in range(4)) + f"amix=inputs=4:normalize=0,apad,atrim=0:{total}[a]"
run("ffmpeg", "-y", "-loglevel", "error", "-i", f"{D}/picture.mp4", *inputs, "-filter_complex", mix,
    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart",
    f"{D}/rgv_news_visual_demo.mp4")
print("demo ok", round(total, 1), "s; shot starts", [round(s, 1) for s in starts])
