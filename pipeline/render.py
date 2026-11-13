"""Render an RGV News episode (episode.json) into:
  - long.mp4      16:9 long-form video (YouTube / Facebook)
  - short.mp4     9:16 vertical Short / Reel with burned-in captions
  - thumb.jpg     1280x720 YouTube thumbnail
Usage: python3 render.py <episode_dir> [--voice-dir DIR]
"""
import json, os, re, subprocess, sys, argparse, math
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import soundfile as sf

FONT_DIR = "/usr/share/fonts/opentype/inter"
F = {
    "black": f"{FONT_DIR}/Inter-Black.otf",
    "xbold": f"{FONT_DIR}/Inter-ExtraBold.otf",
    "bold": f"{FONT_DIR}/Inter-Bold.otf",
    "semi": f"{FONT_DIR}/Inter-SemiBold.otf",
    "med": f"{FONT_DIR}/Inter-Medium.otf",
}
BG_TOP = (9, 16, 32)
BG_BOT = (17, 30, 52)
INK = (241, 245, 249)
MUTED = (148, 163, 184)
BRAND = (249, 115, 22)        # orange
TONE = {"up": (52, 211, 153), "down": (251, 191, 36), None: BRAND}
FPS = 30
GAP = 0.35  # seconds of silence after each scene


def font(name, size):
    return ImageFont.truetype(F[name], size)


def wrap(draw, text, fnt, max_w):
    lines = []
    for para in text.split("\n"):
        words, cur = para.split(), ""
        for w in words:
            t = (cur + " " + w).strip()
            if draw.textlength(t, font=fnt) <= max_w:
                cur = t
            else:
                if cur:
                    lines.append(cur)
                cur = w
        lines.append(cur)
    return lines


def fit_font(draw, text, name, size, max_w, max_lines, min_size=40):
    while size > min_size:
        f = font(name, size)
        if len(wrap(draw, text, f, max_w)) <= max_lines and all(
            draw.textlength(l, font=f) <= max_w for l in wrap(draw, text, f, max_w)):
            return f
        size -= 4
    return font(name, min_size)


def draw_lines(draw, lines, fnt, x, y, fill, spacing=1.15, anchor_center=False, W=None):
    lh = int(fnt.size * spacing)
    for l in lines:
        if anchor_center:
            draw.text((W // 2, y), l, font=fnt, fill=fill, anchor="ma")
        else:
            draw.text((x, y), l, font=fnt, fill=fill)
        y += lh
    return y


def background(W, H, accent):
    arr = np.zeros((H, W, 3), dtype=np.float32)
    t = np.linspace(0, 1, H)[:, None]
    for c in range(3):
        arr[:, :, c] = BG_TOP[c] * (1 - t) + BG_BOT[c] * t
    # soft accent glow, top-right
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt((xx - W * 0.9) ** 2 + (yy - H * 0.05) ** 2) / max(W, H)
    glow = np.clip(1 - d * 1.6, 0, 1) ** 2 * 0.22
    for c in range(3):
        arr[:, :, c] += glow * (accent[c] - arr[:, :, c])
    img = Image.fromarray(arr.clip(0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    step = 80
    for x in range(0, W, step):
        d.line([(x, 0), (x, H)], fill=(255, 255, 255, 8), width=1)
    img = Image.blend(img, Image.fromarray(arr.clip(0, 255).astype(np.uint8)), 0.85)
    return img


def chrome(img, d, W, H, date_str, accent, vertical):
    m = 64 if not vertical else 72
    # brand mark
    bx, by = m, H - m - 44 if not vertical else 110
    d.rounded_rectangle([bx, by, bx + 14, by + 44], 3, fill=BRAND)
    d.text((bx + 28, by + 2), "RGV NEWS", font=font("black", 34), fill=INK)
    d.text((W - m, by + 8), date_str, font=font("semi", 26), fill=MUTED, anchor="ra")
    # accent rule
    d.rectangle([0, 0, W, 8], fill=accent)


def pill(d, x, y, text, color, size=30, anchor_center=False, W=None):
    f = font("black", size)
    tw = d.textlength(text, font=f)
    pad_x, pad_y = int(size * 0.7), int(size * 0.45)
    w, h = tw + 2 * pad_x, size + 2 * pad_y
    if anchor_center:
        x = (W - w) / 2
    d.rounded_rectangle([x, y, x + w, y + h], h // 2, fill=color)
    d.text((x + pad_x, y + pad_y - size * 0.08), text, font=f, fill=BG_TOP)
    return y + h


def render_slide(scene, W, H, date_str, vertical=False):
    tone = scene.get("tone")
    accent = TONE.get(tone, BRAND)
    img = background(W, H, accent)
    d = ImageDraw.Draw(img)
    chrome(img, d, W, H, date_str, accent, vertical)
    img = img.convert("RGBA")
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    m = 120 if not vertical else 90
    maxw = W - 2 * m
    t = scene["type"]
    # vertical: content lives in the upper ~62% so captions can sit below
    top = 260 if vertical else 150
    area_h = (H * 0.60 - top) if vertical else (H - 150 - top - 60)

    if t in ("title", "outro"):
        y = top + (area_h * 0.18 if not vertical else 120)
        if scene.get("kicker"):
            y = pill(d, m, y, scene["kicker"], accent, 30 if not vertical else 36,
                     anchor_center=vertical, W=W) + 50
        f = fit_font(d, scene["headline"], "black", 118 if not vertical else 104, maxw, 4)
        y = draw_lines(d, wrap(d, scene["headline"], f, maxw), f, m, y, INK, 1.08,
                       anchor_center=vertical, W=W) + 30
        if scene.get("sub"):
            fs = font("semi", 42 if not vertical else 46)
            draw_lines(d, wrap(d, scene["sub"], fs, maxw), fs, m, y, MUTED, 1.3,
                       anchor_center=vertical, W=W)

    elif t == "section":
        y = top + (area_h * 0.25 if not vertical else 160)
        y = pill(d, m, y, scene["tag"], accent, 34 if not vertical else 40,
                 anchor_center=vertical, W=W) + 50
        f = fit_font(d, scene["headline"], "black", 104 if not vertical else 96, maxw, 4)
        draw_lines(d, wrap(d, scene["headline"], f, maxw), f, m, y, INK, 1.08,
                   anchor_center=vertical, W=W)

    elif t == "stat":
        y = top + (area_h * 0.08 if not vertical else 80)
        fl = font("bold", 40 if not vertical else 42)
        y = draw_lines(d, wrap(d, scene["label"].upper(), fl, maxw), fl, m, y, accent, 1.2,
                       anchor_center=vertical, W=W) + 20
        fb = fit_font(d, scene["big"], "black", 220 if not vertical else 190, maxw, 1, 80)
        y = draw_lines(d, [scene["big"]], fb, m, y, INK, 1.0, anchor_center=vertical, W=W)
        if scene.get("unit"):
            fu = font("bold", 56 if not vertical else 58)
            y = draw_lines(d, [scene["unit"]], fu, m, y + 10, INK, 1.2,
                           anchor_center=vertical, W=W)
        y += 40
        d.rectangle([m if not vertical else W // 2 - 60, y,
                     (m + 120) if not vertical else W // 2 + 60, y + 6], fill=accent)
        y += 50
        fc = font("med", 40 if not vertical else 40)
        draw_lines(d, wrap(d, scene.get("caption", ""), fc, maxw), fc, m, y, MUTED, 1.35,
                   anchor_center=vertical, W=W)

    elif t == "split":
        y = top + 30
        fl = font("bold", 40)
        y = draw_lines(d, wrap(d, scene["label"].upper(), fl, maxw), fl, m, y, accent, 1.2,
                       anchor_center=vertical, W=W) + 50
        items = scene["items"]
        if not vertical:
            gap = 40
            cw = (maxw - gap * (len(items) - 1)) / len(items)
            for i, (big, small) in enumerate(items):
                x = m + i * (cw + gap)
                d.rounded_rectangle([x, y, x + cw, y + 420], 28, fill=(20, 32, 56),
                                    outline=(51, 65, 85), width=3)
                fb = fit_font(d, big, "black", 120, cw - 60, 1, 60)
                d.text((x + 40, y + 60), big, font=fb, fill=INK)
                fs = font("semi", 38)
                draw_lines(d, wrap(d, small, fs, cw - 80), fs, x + 40, y + 230, MUTED, 1.3)
        else:
            for big, small in items:
                d.rounded_rectangle([m, y, W - m, y + 250], 28, fill=(20, 32, 56), outline=(51, 65, 85), width=3)
                fb = fit_font(d, big, "black", 110, maxw - 80, 1, 60)
                d.text((m + 40, y + 30), big, font=fb, fill=INK)
                d.text((m + 40, y + 165), small, font=font("semi", 38), fill=MUTED)
                y += 280

    elif t == "bullets":
        y = top + (30 if not vertical else 40)
        fh = fit_font(d, scene["headline"], "black", 84 if not vertical else 76, maxw, 2)
        y = draw_lines(d, wrap(d, scene["headline"], fh, maxw), fh, m, y, INK, 1.1) + 50
        fb = font("semi", 52 if not vertical else 50)
        for b in scene["bullets"]:
            d.rounded_rectangle([m, y + 14, m + 22, y + 36], 6, fill=accent)
            y = draw_lines(d, wrap(d, b, fb, maxw - 60), fb, m + 56, y, INK, 1.25) + 34
    # center the content block vertically in its region
    bb = layer.getbbox()
    if bb:
        r0, r1 = (230, H * 0.64) if vertical else (90, H - 150)
        dy = int((r0 + r1) / 2 - (bb[1] + bb[3]) / 2)
        shifted = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        shifted.paste(layer, (0, dy), layer)
        layer = shifted
    return Image.alpha_composite(img, layer)


def tts(engine, text, voice, speed, out):
    samples, sr = engine.create(text, voice=voice, speed=speed, lang="en-us")
    pad = np.zeros(int(sr * GAP), dtype=samples.dtype)
    sf.write(out, np.concatenate([samples, pad]), sr)
    return len(samples) / sr + GAP


def premade(src, out):
    """Use a pre-generated narration clip (e.g. ElevenLabs mp3): convert to wav and add the gap."""
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-af",
                    f"apad=pad_dur={GAP}", "-ar", "48000", "-ac", "1", out], check=True)
    d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                       "-of", "csv=p=0", out]).decode().strip())
    return d


def narrate(eng, ed, name, text, voice, speed, out):
    """Prefer episodes/<date>/audio/<name>.mp3 if present; otherwise use the free local voice."""
    src = f"{ed}/audio/{name}.mp3"
    if os.path.exists(src):
        return premade(src, out)
    if eng is None:
        raise SystemExit(f"missing narration clip {src} and no local voice model loaded")
    return tts(eng, text, voice, speed, out)


def clip(img_path, wav, dur, out, W, H):
    frames = int(math.ceil(dur * FPS))
    # slow push-in: 1.00 -> 1.04 over the scene, rendered from a 2x source for smoothness
    zf = f"zoompan=z='1+0.04*on/{frames}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps={FPS}"
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", img_path, "-i", wav,
        "-vf", f"scale={W*2}:{H*2},{zf},format=yuv420p",
        "-frames:v", str(frames), "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-shortest", out], check=True)


def concat(parts, out):
    lst = out + ".txt"
    with open(lst, "w") as f:
        for p in parts:
            f.write(f"file '{os.path.abspath(p)}'\n")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                    "-i", lst, "-c", "copy", "-movflags", "+faststart", out], check=True)
    os.remove(lst)


def ass_time(t):
    h, r = divmod(t, 3600); m_, s = divmod(r, 60)
    return f"{int(h)}:{int(m_):02d}:{s:05.2f}"


def captions_ass(segments, out, W, H):
    """segments: list of (start, dur, narration). Chunks of ~4 words, timed by character share."""
    hdr = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Inter Black,78,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,6,0,2,80,80,{int(H*0.24)},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    for start, dur, text in segments:
        speak = dur - GAP
        words = text.split()
        chunks, cur = [], []
        for w in words:
            cur.append(w)
            if len(cur) >= 4 or re.search(r"[.,:;?!]$", w):
                chunks.append(" ".join(cur)); cur = []
        if cur:
            chunks.append(" ".join(cur))
        total = sum(len(c) + 2 for c in chunks)
        t = start
        for c in chunks:
            d = speak * (len(c) + 2) / total
            ev.append(f"Dialogue: 0,{ass_time(t)},{ass_time(t + d)},Cap,,0,0,0,,{c.upper()}")
            t += d
    with open(out, "w") as f:
        f.write(hdr + "\n".join(ev) + "\n")


def thumbnail(ep, out):
    W, H = 1280, 720
    img = background(W, H, BRAND)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 10], fill=BRAND)
    d.rounded_rectangle([60, 56, 74, 100], 3, fill=BRAND)
    d.text((88, 58), "RGV NEWS", font=font("black", 40), fill=INK)
    head = ep.get("thumb_text", "2 BIG OPPORTUNITIES\n1 RISK TO WATCH")
    f = fit_font(d, head, "black", 120, W - 120, 3)
    y = draw_lines(d, wrap(d, head, f, W - 120), f, 60, 170, INK, 1.05)
    pill(d, 60, y + 30, ep.get("thumb_pill", "RIO GRANDE VALLEY · " + ep["date"]), BRAND, 34)
    img.convert("RGB").save(out, quality=92)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episode_dir")
    ap.add_argument("--voice-dir", default=os.environ.get("KOKORO_DIR", "./models"))
    a = ap.parse_args()
    ed = a.episode_dir
    eng = None
    if os.path.exists(f"{a.voice_dir}/kokoro-v1.0.onnx"):
        from kokoro_onnx import Kokoro
        eng = Kokoro(f"{a.voice_dir}/kokoro-v1.0.onnx", f"{a.voice_dir}/voices-v1.0.bin")
    ep = json.load(open(f"{ed}/episode.json"))
    work = f"{ed}/build"; os.makedirs(work, exist_ok=True)
    from datetime import date
    date_str = date.fromisoformat(ep["date"]).strftime("%b %-d, %Y").upper()
    voice, speed = ep.get("voice", "am_michael"), ep.get("speed", 1.0)

    # ---- long form ----
    parts, durs = [], []
    for i, sc in enumerate(ep["scenes"]):
        wav = f"{work}/a{i:02d}.wav"; png = f"{work}/s{i:02d}.png"; mp4 = f"{work}/c{i:02d}.mp4"
        dur = narrate(eng, ed, f"scene_{i:02d}", sc["narration"], voice, speed, wav)
        render_slide(sc, 1920, 1080, date_str).convert("RGB").save(png)
        clip(png, wav, dur, mp4, 1920, 1080)
        parts.append(mp4); durs.append(dur)
        print(f"scene {i}: {dur:.1f}s", flush=True)
    concat(parts, f"{ed}/long.mp4")
    # chapter timestamps for the description
    t, chapters = 0.0, []
    for sc, dur in zip(ep["scenes"], durs):
        if sc["type"] in ("title", "section"):
            name = "Intro" if sc["type"] == "title" else f'{sc["tag"].title()}: {sc["headline"]}'
            chapters.append(f"{int(t//60):02d}:{int(t%60):02d} {name}")
        t += dur
    json.dump({"chapters": chapters, "duration": t}, open(f"{ed}/long_meta.json", "w"), indent=1)

    # ---- short ----
    sh = ep.get("short")
    if sh:
        scenes = [sh["hook"]] + [ep["scenes"][k] for k in sh["scene_indexes"]] + [sh["cta"]]
        names = ["short_hook"] + [f"scene_{k:02d}" for k in sh["scene_indexes"]] + ["short_cta"]
        sparts, segs, t = [], [], 0.0
        for i, (sc, nm) in enumerate(zip(scenes, names)):
            wav = f"{work}/va{i:02d}.wav"; png = f"{work}/vs{i:02d}.png"; mp4 = f"{work}/vc{i:02d}.mp4"
            dur = narrate(eng, ed, nm, sc["narration"], voice, speed * 1.05, wav)
            render_slide(sc, 1080, 1920, date_str, vertical=True).convert("RGB").save(png)
            clip(png, wav, dur, mp4, 1080, 1920)
            sparts.append(mp4); segs.append((t, dur, sc["narration"])); t += dur
        concat(sparts, f"{work}/short_raw.mp4")
        captions_ass(segs, f"{work}/short.ass", 1080, 1920)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{work}/short_raw.mp4",
                        "-vf", f"ass={work}/short.ass:fontsdir={FONT_DIR}", "-c:v", "libx264",
                        "-preset", "medium", "-crf", "20", "-c:a", "copy",
                        "-movflags", "+faststart", f"{ed}/short.mp4"], check=True)
        print(f"short: {t:.1f}s")

    thumbnail(ep, f"{ed}/thumb.jpg")
    print("done")


if __name__ == "__main__":
    main()
