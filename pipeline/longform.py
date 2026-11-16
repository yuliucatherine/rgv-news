"""Long-form episode assembler (16:9, 1920x1080; frame rate from the timeline's "fps", default 30).
A timeline JSON lists blocks; each block = optional narration clip + one or more visuals
(videos, Blender renders, photos, generated cards) + text layers (headline, kinetic words,
captions from the narration text, source credit) + optional natural sound.
Usage: python3 longform.py <timeline.json>  [--only i,j]  (renders block segments, then joins)
"""
import sys, os, json, math, re, subprocess, hashlib
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

W, H, FPS = 1920, 1080, 30
FD = "/usr/share/fonts/opentype/inter"
NAVY = (9, 16, 32); INK = (241, 245, 249); SUB = (203, 213, 225); ORANGE = (249, 115, 22)
TEAL = (52, 211, 153); BLUE = (56, 189, 248)


def F(w, s): return ImageFont.truetype(f"{FD}/Inter-{w}.otf", s)
def run(*a): subprocess.run([str(x) for x in a], check=True)
def probe_dur(p): return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]))


def is_portrait(p):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                   "stream=width,height:stream_side_data=rotation", "-of", "json", p]).decode()
    s = json.loads(out)["streams"][0]; w, h = s["width"], s["height"]
    rot = 0
    for sd in s.get("side_data_list", []) or []:
        if "rotation" in sd: rot = abs(int(sd["rotation"]))
    if rot in (90, 270): w, h = h, w
    return h > w


# ---------------------------------------------------------------- cards (PIL)
def card_bg(accent=ORANGE):
    t = np.linspace(0, 1, H)[:, None, None]
    arr = (np.array(NAVY) * (1 - t) + np.array((17, 30, 52)) * t) * np.ones((H, W, 3))
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt((xx - W * 0.85) ** 2 + (yy - H * 0.1) ** 2) / W
    g = np.clip(1 - d * 1.5, 0, 1) ** 2 * 0.25
    arr = arr + g[..., None] * (np.array(accent) - arr)
    im = Image.fromarray(arr.clip(0, 255).astype(np.uint8)); dr = ImageDraw.Draw(im, "RGBA")
    for x in range(0, W, 96): dr.line([(x, 0), (x, H)], fill=(255, 255, 255, 10))
    for y in range(0, H, 96): dr.line([(0, y), (W, y)], fill=(255, 255, 255, 10))
    return im


def wrap(dr, text, fnt, maxw):
    out = []
    for para in text.split("\n"):
        cur = ""
        for w in para.split():
            t = (cur + " " + w).strip()
            if dr.textlength(t, font=fnt) <= maxw: cur = t
            else: out.append(cur); cur = w
        out.append(cur)
    return out


def make_card(spec, path):
    kind = spec["type"]; acc = {"orange": ORANGE, "teal": TEAL, "blue": BLUE}.get(spec.get("accent", "orange"), ORANGE)
    im = card_bg(acc); d = ImageDraw.Draw(im, "RGBA"); m = 160
    if kind == "title":
        d.rounded_rectangle([m, 360, m + 18, 470], 4, fill=ORANGE)
        f = F("Black", 120); y = 340
        for l in wrap(d, spec["title"], f, W - 2 * m - 60): d.text((m + 50, y), l, font=f, fill=INK); y += 130
        if spec.get("sub"): d.text((m + 50, y + 20), spec["sub"], font=F("SemiBold", 52), fill=SUB)
    elif kind == "section":
        f1 = F("Black", 40); tw = d.textlength(spec["tag"], font=f1)
        d.rounded_rectangle([m, 400, m + tw + 60, 470], 35, fill=acc)
        d.text((m + 30, 412), spec["tag"], font=f1, fill=NAVY)
        f = F("Black", 110); y = 500
        for l in wrap(d, spec["title"], f, W - 2 * m): d.text((m, y), l, font=f, fill=INK); y += 120
    elif kind == "quote":
        d.text((m - 20, 170), "“", font=F("Black", 260), fill=acc)
        f = F("Bold", 76); y = 360
        for l in wrap(d, spec["quote"], f, W - 2 * m): d.text((m, y), l, font=f, fill=INK); y += 96
        d.text((m, y + 40), spec["by"], font=F("SemiBold", 40), fill=SUB)
        if spec.get("source"): d.text((m, y + 100), spec["source"], font=F("Medium", 30), fill=(148, 163, 184))
    elif kind == "list":
        d.text((m, 200), spec["title"], font=F("Black", 84), fill=INK)
        d.rectangle([m, 320, m + 140, 328], fill=acc)
        f = F("SemiBold", 54); y = 400
        for b in spec["items"]:
            d.rounded_rectangle([m, y + 16, m + 26, y + 42], 6, fill=acc)
            for l in wrap(d, b, f, W - 2 * m - 80): d.text((m + 60, y), l, font=f, fill=INK); y += 70
            y += 34
    elif kind == "stat":
        d.text((m, 250), spec.get("label", "").upper(), font=F("Bold", 44), fill=acc)
        fb = F("Black", 230); d.text((m, 310), spec["big"], font=fb, fill=INK)
        y = 600
        for l in spec.get("lines", []):
            d.text((m, y), l, font=F("SemiBold", 52), fill=SUB); y += 74
    elif kind == "timeline":
        d.text((m, 200), spec["title"], font=F("Black", 84), fill=INK)
        pts = spec["points"]; x0, x1, yl = m + 230, W - m - 230, 620
        d.line([(x0, yl), (x1, yl)], fill=(71, 85, 105), width=8)
        for i, (big, small) in enumerate(pts):
            x = x0 + (x1 - x0) * i / max(1, len(pts) - 1)
            col = acc if i == len(pts) - 1 else INK
            d.ellipse([x - 26, yl - 26, x + 26, yl + 26], fill=col)
            d.text((x, yl - 80), big, font=F("Black", 64), fill=col, anchor="ms")
            d.text((x, yl + 90), small, font=F("SemiBold", 40), fill=SUB, anchor="ma")
    if spec.get("footer"): d.text((W - 60, H - 50), spec["footer"], font=F("Medium", 26), fill=(148, 163, 184), anchor="rs")
    im.save(path)


# ---------------------------------------------------------------- overlay PNGs
def scrims(tmp):
    top = os.path.join(tmp, "scrim_top.png"); left = os.path.join(tmp, "scrim_left.png"); bot = os.path.join(tmp, "scrim_bot.png")
    if not os.path.exists(top):
        a = np.zeros((H, W, 4), np.uint8); a[..., :3] = NAVY
        y = np.arange(H); a[..., 3] = (np.clip(1 - y / 270, 0, 1) ** 1.6 * 205)[:, None]
        Image.fromarray(a).save(top)
        b = np.zeros((H, W, 4), np.uint8); b[..., :3] = NAVY
        x = np.arange(W); b[..., 3] = (np.clip(1 - x / (W * 0.5), 0, 1) ** 1.5 * 200)[None, :]
        Image.fromarray(b).save(left)
        c = np.zeros((H, W, 4), np.uint8); c[..., :3] = NAVY
        c[..., 3] = (np.clip((y - (H - 260)) / 260, 0, 1) ** 1.5 * 150)[:, None]
        Image.fromarray(c).save(bot)
    return top, left, bot


# ---------------------------------------------------------------- captions
def caption_chunks(text, maxc=44):
    words = text.replace("—", "-").split(); out, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if len(t) > maxc and cur: out.append(cur); cur = w
        else: cur = t
        if re.search(r"[.?!:]$", w) and len(cur) > 18: out.append(cur); cur = ""
    if cur: out.append(cur)
    return out


def esc_path(p): return p.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")


def drawtext(tmp, text, x, y, size, font="Bold", color="white", a=0.0, b=1e9, fade=0.25, box=None, alpha_max=1.0):
    h = hashlib.md5(text.encode()).hexdigest()[:10]; tf = os.path.join(tmp, f"t_{h}.txt")
    open(tf, "w").write(text)
    alpha = f"{alpha_max}*if(lt(t,{a}+{fade}),max(0,(t-{a})/{fade}),if(gt(t,{b}-{fade}),max(0,({b}-t)/{fade}),1))"
    s = (f"drawtext=fontfile={FD}/Inter-{font}.otf:textfile='{esc_path(tf)}':x={x}:y={y}:fontsize={size}:expansion=none"
         f":fontcolor={color}:alpha='{alpha}':enable='between(t,{a},{b})'")
    if box: s += f":box=1:boxcolor={box}:boxborderw=18"
    return s


# ---------------------------------------------------------------- block renderer
def probe_fps(src):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=avg_frame_rate",
                        "-of", "csv=p=0", src], capture_output=True, text=True).stdout.strip()
    try:
        a, b = r.split("/"); return float(a) / float(b)
    except Exception:
        return 30.0


def visual_filter(i, v, alloc, vin):
    """returns (input_args, filter_string producing [v{i}])"""
    args, fl = [], ""
    if "video" in v:
        src = v["video"]; ss = v.get("ss", 0.0)
        avail = probe_dur(src) - ss
        ln = min(v.get("len", avail), avail)
        f = alloc / ln
        if f > 1.15 and probe_fps(src) < 50:
            print(f"  warn: {os.path.basename(src)} slowed x{f:.2f} (will look choppy; smooth it with pipeline/smooth.py)")
        args = ["-ss", f"{ss}", "-t", f"{ln + 0.2}", "-i", src]
        base = f"[{vin}:v]setpts=PTS-STARTPTS,setpts={f:.5f}*PTS,fps={FPS}"
        if is_portrait(src):
            fl = (f"{base},split[a{i}][b{i}];[a{i}]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                  f"gblur=sigma=40,eq=brightness=-0.12:saturation=0.8[bg{i}];[b{i}]scale=-2:{H}[fg{i}];"
                  f"[bg{i}][fg{i}]overlay=(W-w)/2:0,trim=duration={alloc},setsar=1[v{i}]")
        else:
            fl = (f"{base},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                  f"trim=duration={alloc},setsar=1[v{i}]")
    else:  # image or card: slow push-in / pan
        src = v["image"]; n = int(alloc * FPS) + 1
        z0, z1 = v.get("zoom", [1.0, 1.08]); px = v.get("pan", [0.5, 0.5, 0.5, 0.5])
        args = ["-loop", "1", "-t", f"{alloc + 0.2}", "-i", src]
        zexpr = f"{z0}+({z1}-{z0})*on/{n}"
        xexpr = f"(iw-iw/zoom)*({px[0]}+({px[2]}-{px[0]})*on/{n})"; yexpr = f"(ih-ih/zoom)*({px[1]}+({px[3]}-{px[1]})*on/{n})"
        pre = f"scale={W*2}:{H*2}:force_original_aspect_ratio=increase,crop={W*2}:{H*2}"
        if v.get("portrait_fill"):
            pre = (f"split[pa{i}][pb{i}];[pa{i}]scale={W*2}:{H*2}:force_original_aspect_ratio=increase,crop={W*2}:{H*2},gblur=sigma=60,"
                   f"eq=brightness=-0.12[pbg{i}];[pb{i}]scale=-2:{H*2}[pfg{i}];[pbg{i}][pfg{i}]overlay=(W-w)/2:0")
        fl = (f"[{vin}:v]{pre},zoompan=z='{zexpr}':x='{xexpr}':y='{yexpr}':d={n}:s={W}x{H}:fps={FPS},"
              f"trim=duration={alloc},setsar=1[v{i}]")
    return args, fl


def render_block(k, b, cfg, tmp):
    out = os.path.join(tmp, f"blk_{k:03d}.mp4")
    pad0, pad1 = b.get("pad", [0.35, 0.55])
    narr = os.path.join(cfg["audio_dir"], b["narr"] + ".mp3") if b.get("narr") else None
    nd = probe_dur(narr) if narr else 0.0
    D = b.get("dur", nd + pad0 + pad1)
    vis = b["visuals"]
    # cards are generated images
    for j, v in enumerate(vis):
        if "card" in v:
            p = os.path.join(tmp, f"card_{k:03d}_{j}.png"); make_card(v["card"], p)
            v.setdefault("zoom", [1.0, 1.035]); v["image"] = p
    wts = [v.get("weight", 1.0) for v in vis]; allocs = [D * w / sum(wts) for w in wts]
    args, fls = [], []
    for i, (v, al) in enumerate(zip(vis, allocs)):
        a, f = visual_filter(i, v, al, i); args += a; fls.append(f)
    nv = len(vis); idx = nv
    top, left, bot = scrims(tmp)
    args += ["-loop", "1", "-i", top, "-loop", "1", "-i", left, "-loop", "1", "-i", bot]
    i_top, i_left, i_bot = idx, idx + 1, idx + 2; idx += 3
    chain = "".join(f"[v{i}]" for i in range(nv)) + f"concat=n={nv}:v=1:a=0[vc]"
    fls.append(chain)
    cur = "vc"
    kin = b.get("kinetic"); head = b.get("headline")
    caps = [] if b.get("no_captions") or not narr else caption_chunks(b.get("text", ""))
    # scrims
    if head:
        fls.append(f"[{cur}][{i_top}:v]overlay=0:0:shortest=1[s1]"); cur = "s1"
    if kin:
        ka = kin.get("at", 0.6); kb = min(D, ka + kin.get("step", 0.4) * len(kin["words"]) + kin.get("hold", 2.0))
        fls.append(f"[{cur}][{i_left}:v]overlay=0:0:shortest=1:enable='between(t,{ka},{kb + 0.3})'[s2]"); cur = "s2"
    if caps:
        fls.append(f"[{cur}][{i_bot}:v]overlay=0:0:shortest=1[s3]"); cur = "s3"
    dts = []
    if head:
        h1, h2 = (head + [""])[:2]
        dts.append(f"drawbox=x=64:y=62:w=14:h=56:color=0xF97316@1:t=fill:enable='between(t,0.2,{D})'")
        dts.append(drawtext(tmp, h1, 96, 60, 50, "Black", "0xF1F5F9", 0.2, D))
        if h2: dts.append(drawtext(tmp, h2, 96, 122, 32, "SemiBold", "0xCBD5E1", 0.4, D))
    if kin:
        words = kin["words"]; ka = kin.get("at", 0.6); st = kin.get("step", 0.4)
        kb = min(D, ka + st * len(words) + kin.get("hold", 2.0))
        size = kin.get("size", 150 if len(words) <= 4 else 118); lh = int(size * 1.02)
        y0 = (H - lh * len(words)) // 2 - 40
        for wi, wd in enumerate(words):
            col = "0xF97316" if (wd.endswith("?") or wd.endswith("!") or wd.startswith("$") or wi == len(words) - 1 and kin.get("last_orange", True)) else "0xF1F5F9"
            dts.append(drawtext(tmp, wd, 110, y0 + wi * lh, size, "Black", col, ka + wi * st, kb, fade=0.2))
    if caps and nd > 0:
        tot = sum(len(c) + 3 for c in caps); t = pad0
        for c in caps:
            dd = nd * (len(c) + 3) / tot
            dts.append(drawtext(tmp, c, "(w-tw)/2", H - 150, 44, "SemiBold", "0xFFFFFF", t, t + dd, fade=0.08, box="0x091020@0.55"))
            t += dd
    if b.get("credit"):
        dts.append(drawtext(tmp, b["credit"], f"w-tw-40", b.get("credit_y", H - 46), 24, "Medium", "0xCBD5E1", 0.0, D, fade=0.3, alpha_max=0.9))
    for extra in b.get("texts", []):   # free-positioned text: {text,x,y,size,font,color,at,until}
        dts.append(drawtext(tmp, extra["text"], extra.get("x", 110), extra.get("y", 300), extra.get("size", 60),
                            extra.get("font", "Black"), extra.get("color", "0xF1F5F9"), extra.get("at", 0.3),
                            extra.get("until", D), box=extra.get("box")))
    if dts:
        fls.append(f"[{cur}]" + ",".join(dts) + "[vo]"); cur = "vo"
    fls.append(f"[{cur}]format=yuv420p,trim=duration={D}[vout]")
    # audio
    aparts = []
    if narr:
        args += ["-i", narr]; ia = idx; idx += 1
        aparts.append(f"[{ia}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={int(pad0*1000)}|{int(pad0*1000)}[an]")
    nat = b.get("natural")
    if nat:
        args += ["-ss", f"{nat.get('ss', 0)}", "-t", f"{D + 0.2}", "-i", nat["src"]]; ib = idx; idx += 1
        aparts.append(f"[{ib}:a]aresample=48000,aformat=channel_layouts=stereo,volume={nat.get('gain', -14)}dB,"
                      f"afade=t=in:d=0.3,afade=t=out:st={max(0, D - 0.5)}:d=0.5[nat]")
    if not aparts:
        args += ["-f", "lavfi", "-t", f"{D}", "-i", "anullsrc=r=48000:cl=stereo"]; ib = idx; idx += 1
        aparts.append(f"[{ib}:a]anull[nat]")
    labels = "".join(x[x.rindex("["):] for x in aparts)
    aparts.append(f"{labels}amix=inputs={len(aparts)}:normalize=0,apad,atrim=duration={D}[aout]")
    fls += aparts
    run("ffmpeg", "-y", "-loglevel", "error", *args, "-filter_complex", ";".join(fls),
        "-map", "[vout]", "-map", "[aout]", "-r", FPS, "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-t", f"{D}", out)
    return out, D


def main():
    global FPS
    tl = json.load(open(sys.argv[1]))
    FPS = int(tl.get("fps", 30))
    only = None
    if "--only" in sys.argv: only = {int(x) for x in sys.argv[sys.argv.index("--only") + 1].split(",")}
    tmp = tl.get("tmp", os.path.splitext(tl["out"])[0] + "_build"); os.makedirs(tmp, exist_ok=True)
    narr_text = {p["id"]: p["text"] for p in json.load(open(tl["narration_json"]))}
    parts, t = [], 0.0; chapters = []
    for k, b in enumerate(tl["blocks"]):
        if b.get("narr"): b.setdefault("text", narr_text[b["narr"]])
        if b.get("chapter"): chapters.append((t, b["chapter"]))
        p = os.path.join(tmp, f"blk_{k:03d}.mp4")
        if only is None or k in only or not os.path.exists(p):
            p, d = render_block(k, b, tl, tmp); print(f"block {k:02d} {d:5.1f}s {b.get('narr', b.get('label', ''))}", flush=True)
        else:
            d = probe_dur(p)
        parts.append(p); t += d
    lst = os.path.join(tmp, "list.txt"); open(lst, "w").write("".join(f"file '{os.path.abspath(p)}'\n" for p in parts))
    joined = os.path.join(tmp, "joined.mp4")
    run("ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", joined)
    run("ffmpeg", "-y", "-loglevel", "error", "-i", joined, "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", tl["out"])
    meta = {"duration": t, "chapters": [[round(a, 1), c] for a, c in chapters]}
    json.dump(meta, open(os.path.splitext(tl["out"])[0] + "_meta.json", "w"), indent=1)
    if tl.get("music"):   # quiet, ducked background music bed (pipeline/music_bed.py)
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import music_bed
        nomusic = os.path.join(tmp, "nomusic.mp4"); os.replace(tl["out"], nomusic)
        music_bed.build(nomusic, meta, tl["music"], tl["out"])
    print("episode ok", tl["out"], f"{t/60:.1f} min")


if __name__ == "__main__":
    main()
