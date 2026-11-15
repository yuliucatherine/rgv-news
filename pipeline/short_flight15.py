"""Vertical Short from the owner's Starship Flight 15 footage (natural sound + on-screen text).
Usage: python3 short_flight15.py <videos_dir> <out_dir>
"""
import sys, os, subprocess, json

V, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True); T = os.path.join(OUT, "seg"); os.makedirs(T, exist_ok=True)
FONT = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
FONT2 = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
W, H, FPS = 1080, 1920, 30
ENC = ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2"]


def run(*a): subprocess.run(list(a), check=True)


segs = []


def seg(name, src, ss, dur, vf_pre="", slow=1.0, gain=0.0):
    """cut [ss, ss+dur] from src, optionally slowed (slow=2 -> half speed, real 60fps frames)."""
    out = f"{T}/{len(segs):02d}_{name}.mp4"
    vf = (vf_pre + "," if vf_pre else "") + f"scale={W}:{H}:flags=lanczos,setsar=1"
    af = f"volume={gain}dB"
    if slow != 1.0:
        vf += f",setpts={slow}*PTS"
        af += f",atempo={1/slow:.4f}"
    vf += f",fps={FPS}"
    run("ffmpeg", "-y", "-loglevel", "error", "-ss", str(ss), "-t", str(dur), "-i", src,
        "-vf", vf, "-af", af, *ENC, out)
    d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                       "-of", "csv=p=0", out]))
    segs.append((out, d)); return d


# ---- stabilize the explosion clip once (cropped to vertical around the action) ----
stab = f"{T}/8769_stab.mp4"
if not os.path.exists(stab):
    crop = "crop=1216:2160:1190:0"
    run("ffmpeg", "-y", "-loglevel", "error", "-ss", "23", "-t", "36", "-i", f"{V}/IMG_8769.MOV",
        "-vf", f"{crop},vidstabdetect=shakiness=6:accuracy=15:result={T}/tr.trf", "-f", "null", "-")
    run("ffmpeg", "-y", "-loglevel", "error", "-ss", "23", "-t", "36", "-i", f"{V}/IMG_8769.MOV",
        "-vf", f"{crop},vidstabtransform=input={T}/tr.trf:smoothing=25:zoom=4,unsharp=5:5:0.6",
        "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-c:a", "copy", stab)

L = f"{V}/IMG_8758.MOV"; X = stab; C = f"{V}/IMG_9179.MOV"
# Day 1: liftoff (real sync), then the climb when the roar reaches the beach (~18 s later)
seg("liftoff", L, 6.0, 14.0)
seg("roar", L, 30.0, 6.0, gain=-3)
# booster coming down (stabilized clip starts at original 0:23)
seg("fall", X, 25.0 - 23, 5.0)
seg("pre", X, 47.5 - 23, 2.5)
seg("fireball_slow", X, 50.0 - 23, 2.5, slow=2.0)
seg("cloud", X, 52.5 - 23, 1.2)
# Day 2: Ship returns and is caught
seg("descent", C, 3.0, 6.0)
seg("catch_slow", C, 9.0, 4.0, slow=2.0)
seg("caught", C, 13.0, 4.0)

# end card
card = f"{T}/99_card.mp4"
run("ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"color=c=0x091020:s={W}x{H}:d=3:r={FPS}",
    "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", "3",
    "-vf", f"drawbox=x=300:y=860:w=14:h=80:color=0xF97316:t=fill,"
           f"drawtext=fontfile={FONT}:text='RGV NEWS':x=335:y=858:fontsize=86:fontcolor=white,"
           f"drawtext=fontfile={FONT2}:text='What Starbase means for the Valley':x=(w-tw)/2:y=980:fontsize=40:fontcolor=0xCBD5E1,"
           f"drawtext=fontfile={FONT2}:text='Follow for the full story':x=(w-tw)/2:y=1040:fontsize=40:fontcolor=0xF97316",
    *ENC, card)
segs.append((card, 3.0))

# concat
lst = f"{T}/list.txt"; open(lst, "w").write("".join(f"file '{os.path.abspath(p)}'\n" for p, _ in segs))
raw = f"{T}/raw.mp4"
run("ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", raw)
starts = []; t = 0
for p, d in segs: starts.append(t); t += d
S = dict(zip([os.path.basename(p)[3:-4] for p, _ in segs], starts))
D = dict(zip([os.path.basename(p)[3:-4] for p, _ in segs], [d for _, d in segs]))
print(json.dumps({k: round(v, 2) for k, v in S.items()}), "total", round(t, 1))


# Vertical safe zone (YouTube Shorts / Facebook Reels): keep text clear of the right-side buttons
# and the bottom caption/title area. Text auto-shrinks to fit SAFE_W and is centred in [SAFE_L, SAFE_R].
SAFE_L, SAFE_R, SAFE_TOP, SAFE_BOTTOM = 60, 940, 220, 1340
from PIL import ImageFont


def fit(text, size, font, box):
    pad = 44 if box else 0
    while size > 28 and ImageFont.truetype(font, size).getlength(text) + pad > (SAFE_R - SAFE_L):
        size -= 2
    return size, ImageFont.truetype(font, size).getlength(text)


def txt(text, a, b, y, size=92, color="white", font=FONT, box=True, fade=0.25):
    size, tw = fit(text, size, font, box)
    y = max(SAFE_TOP, min(y, SAFE_BOTTOM - size))
    x = int(SAFE_L + ((SAFE_R - SAFE_L) - tw) / 2)
    alpha = f"if(lt(t,{a}+{fade}),(t-{a})/{fade},if(gt(t,{b}-{fade}),({b}-t)/{fade},1))"
    s = (f"drawtext=fontfile={font}:text='{text}':x={x}:y={y}:fontsize={size}:fontcolor={color}"
         f":alpha='{alpha}':enable='between(t,{a},{b})'")
    if box: s += ":box=1:boxcolor=0x091020@0.62:boxborderw=22"
    return s


f = []
# hook: three lines stacking in
h0 = S["liftoff"]
f += [txt("2 DAYS AT STARBASE", h0 + 0.2, h0 + 4.6, 300, 96),
      txt("1 EXPLOSION", h0 + 1.2, h0 + 4.6, 430, 96, "0xF97316"),
      txt("1 HISTORIC CATCH", h0 + 2.2, h0 + 4.6, 560, 96)]
f += [txt("NOV 13 · STARSHIP FLIGHT 15", h0 + 5.0, h0 + 9.5, 300, 64)]
f += [txt("LIFTOFF", h0 + 8.0, h0 + 13.6, 1180, 120)]
f += [txt("THE ROAR HITS THE BEACH", S["roar"] + 0.1, S["roar"] + D["roar"], 300, 70),
      txt("~18 SECONDS LATER", S["roar"] + 0.6, S["roar"] + D["roar"], 410, 70, "0xF97316")]
f += [txt("THE BOOSTER CATCH", S["fall"] + 0.2, S["fall"] + D["fall"], 300, 76),
      txt("WAS CALLED OFF", S["fall"] + 0.7, S["fall"] + D["fall"], 420, 76, "0xF97316")]
f += [txt("BOOM.", S["fireball_slow"] + 0.3, S["cloud"] + D["cloud"], 1150, 150, "0xF97316", box=False)]
f += [txt("NOV 14 · 22.5 HOURS LATER", S["descent"] + 0.2, S["descent"] + 5.8, 300, 64),
      txt("THE SHIP COMES HOME", S["descent"] + 1.2, S["descent"] + 5.8, 410, 70, "0xF97316")]
f += [txt("CAUGHT.", S["catch_slow"] + 4.6, S["caught"] + D["caught"], 1140, 160, "0xF97316", box=False),
      txt("FIRST-EVER SHIP TOWER CATCH", S["caught"] + 0.2, S["caught"] + D["caught"], 300, 62),
      txt("Source: Aviation Week", S["caught"] + 0.4, S["caught"] + D["caught"], 400, 34, "0xCBD5E1", FONT2, box=False)]
f += [txt("Filmed by RGV News · Starbase, TX", 0.5, S["card"] - 0.2, 1300, 30, "0xE2E8F0", FONT2, box=False)]

final = os.path.join(OUT, "short_flight15.mp4")
run("ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-vf", ",".join(f),
    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", *ENC, "-movflags", "+faststart", final)
print("ok", final)
