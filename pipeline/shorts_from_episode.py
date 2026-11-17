"""Vertical Short (1080x1920, 60 fps) cut from a long episode's blocks.
Layout (all text inside the Shorts/Reels/TikTok safe zone x 60-1020, y 220-1340):
  brand chip + big hook headline at the top, the episode's clean 16:9 visuals in the middle
  (no burned-in episode text), big word-chunk captions under it, a source credit, and a closing
  "full breakdown on YouTube" line. Background: blurred, darkened copy of the same footage.
Usage: python3 pipeline/shorts_from_episode.py <short.json>
config: {"timeline": ".../timeline.json", "blocks": [28, 29, 33], "out": "demo/shorts/s1.mp4",
         "hook": ["LINE 1", "LINE 2", "*ORANGE LINE*"], "credit": "Source: ...",
         "music": {"track": "assets/music/X.mp3", "offset": 30}, "end_text": "..."}
"""
import sys, os, json, copy, subprocess, shutil, hashlib
from PIL import ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import longform

W, H, FPS = 1080, 1920, 60
FD = "/usr/share/fonts/opentype/inter"
SAFE_L, SAFE_R, SAFE_TOP, SAFE_BOT = 60, 1020, 220, 1340
VID_Y = 600                       # 16:9 picture: 1080x608 at y 600..1208
CAP_Y = 1236                      # captions centered here (inside the safe zone)


def fit_size(text, font, size, maxw):
    while size > 20 and ImageFont.truetype(f"{FD}/Inter-{font}.otf", size).getlength(text) > maxw:
        size -= 2
    return size


def dt(tmp, text, x, y, size, font="Black", color="white", a=0.0, b=1e9, border=0, box=None, fade=0.15):
    h = hashlib.md5((text + font).encode()).hexdigest()[:10]; tf = os.path.join(tmp, f"v_{h}.txt")
    open(tf, "w").write(text)
    alpha = f"if(lt(t,{a}+{fade}),max(0,(t-{a})/{fade}),if(gt(t,{b}-{fade}),max(0,({b}-t)/{fade}),1))"
    s = (f"drawtext=fontfile={FD}/Inter-{font}.otf:textfile='{tf}':expansion=none:x={x}:y={y}:fontsize={size}"
         f":fontcolor={color}:alpha='{alpha}':enable='between(t,{a},{b})'")
    if border: s += f":borderw={border}:bordercolor=0x091020"
    if box: s += f":box=1:boxcolor={box}:boxborderw=16"
    return s


def main(cfg):
    tl = json.load(open(cfg["timeline"]))
    out = cfg["out"]; base = os.path.splitext(out)[0]
    tmp = base + "_work"; reuse = os.environ.get("REUSE") and os.path.exists(os.path.join(tmp, "clean.mp4"))
    if not reuse: shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
    # 1) clean 16:9 sub-episode from the chosen blocks (episode text stripped, music bed added)
    sub = {k: v for k, v in tl.items() if k not in ("blocks", "music", "out", "tmp")}
    sub["fps"] = FPS; sub["out"] = os.path.join(tmp, "clean.mp4"); sub["tmp"] = os.path.join(tmp, "build")
    blocks = []
    for i in cfg["blocks"]:
        b = copy.deepcopy(tl["blocks"][i])
        for key in ("headline", "kinetic", "texts", "credit", "chapter"): b.pop(key, None)
        b["no_captions"] = True; blocks.append(b)
    blocks[-1]["pad"] = [blocks[-1].get("pad", [0.5, 0.8])[0], 2.6]      # room for the closing line
    sub["blocks"] = blocks
    m = cfg.get("music")
    if m: sub["music"] = {"level_lufs": -27, "segments": [{"track": m["track"], "at": 0, "offset": m.get("offset", 0)}]}
    sj = os.path.join(tmp, "sub.json"); json.dump(sub, open(sj, "w"))
    if not reuse:   # REUSE=1 re-composes the vertical layout without re-rendering the episode blocks
        subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "longform.py"), sj],
                       check=True)
    # 2) caption timing, mirroring longform's own split (narration starts after pad[0])
    narr = {p["id"]: p["text"] for p in json.load(open(tl["narration_json"]))}
    caps, t0 = [], 0.0
    for k, b in enumerate(blocks):
        D = longform.probe_dur(os.path.join(sub["tmp"], f"blk_{k:03d}.mp4"))
        if b.get("narr"):
            mp3 = os.path.join(tl["audio_dir"], f"{b['narr']}.mp3")
            nd = longform.probe_dur(mp3); pad0 = b.get("pad", [0.5, 0.8])[0]
            chunks = longform.caption_chunks(narr[b["narr"]], maxc=cfg.get("cap_chars", 22))
            tot = sum(len(c) + 3 for c in chunks); t = t0 + pad0
            for c in chunks:
                d = nd * (len(c) + 3) / tot; caps.append((t, t + d, c)); t += d
        t0 += D
    total = longform.probe_dur(sub["out"])
    # 3) vertical composition
    dts = []
    chip = "RGV NEWS"
    dts.append(f"drawbox=x={SAFE_L}:y={SAFE_TOP + 8}:w=196:h=52:color=0xF97316@1:t=fill")
    dts.append(dt(tmp, chip, SAFE_L + 20, SAFE_TOP + 20, 30, "Black", "0x091020"))
    dts.append(dt(tmp, cfg.get("chip_sub", "INVESTOR BRIEF"), SAFE_L + 216, SAFE_TOP + 20, 28, "Bold", "0xF1F5F9"))
    y = SAFE_TOP + 92
    for line in cfg["hook"]:
        orange = line.startswith("*") and line.endswith("*"); txt = line.strip("*")
        size = fit_size(txt, "Black", 84, SAFE_R - SAFE_L)
        dts.append(dt(tmp, txt, SAFE_L, y, size, "Black", "0xF97316" if orange else "0xF8FAFC", 0.0, total, border=4))
        y += int(size * 1.08)
    if y > VID_Y - 10: raise SystemExit(f"hook too tall ({y}px); shorten it")
    for a, b, c in caps:
        size = fit_size(c, "Black", 62, SAFE_R - SAFE_L)
        dts.append(dt(tmp, c, "(w-tw)/2", CAP_Y - size // 2, size, "Black", "0xFFFFFF", a, b, border=6, fade=0.05))
    if cfg.get("credit"):
        dts.append(dt(tmp, cfg["credit"], f"{SAFE_R}-tw", VID_Y + 608 - 40, 24, "Medium", "0xE2E8F0", 0, total, border=3))
    end = cfg.get("end_text", "Full 10-minute breakdown on our YouTube channel")
    es = fit_size(end, "Black", 50, SAFE_R - SAFE_L - 40)
    dts.append(dt(tmp, end, "(w-tw)/2", CAP_Y - es // 2, es, "Black", "0xFFFFFF", total - 2.4, total,
                  box="0x091020@0.85", fade=0.3))
    fl = (f"[0:v]split[a][b];[a]scale=-2:{H},crop={W}:{H},gblur=sigma=40,eq=brightness=-0.22:saturation=0.7[bg];"
          f"[b]scale={W}:608[fg];[bg][fg]overlay=0:{VID_Y},drawbox=x=0:y=0:w={W}:h={VID_Y}:color=0x091020@0.9:t=fill,"
          f"drawbox=x=0:y={VID_Y}:w={W}:h=3:color=0xF97316@1:t=fill,drawbox=x=0:y={VID_Y + 605}:w={W}:h=3:color=0xF97316@1:t=fill,"
          + ",".join(dts) + ",format=yuv420p[v]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", sub["out"], "-filter_complex", fl, "-map", "[v]",
                    "-map", "0:a", "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "19",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out], check=True)
    json.dump({"duration": total, "captions": caps}, open(base + "_meta.json", "w"), indent=1)
    print("short ok", out, f"{total:.1f}s")


if __name__ == "__main__":
    main(json.load(open(sys.argv[1])))
