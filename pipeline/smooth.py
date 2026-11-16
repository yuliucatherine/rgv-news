"""Make a 3D shot play smoothly when it is held on screen longer than it was rendered.

The long-form editor stretches a clip to fill its narration block. A 6 s, 24 fps Blender render held
for 18 s plays at ~8 fps and looks choppy. This tool slows the RAW render (no text) with motion-
compensated interpolation to `stretch` x its length at $FPS (default 30), re-times labels.json to the new frame
count, then re-runs overlay.py, so the overlay text is crisp and never interpolated.

Usage:
  python3 pipeline/smooth.py overlay <shot_overlay.json> <stretch> <out.mp4>
  python3 pipeline/smooth.py video <in.mp4> <stretch> <out.mp4>         (2D animations such as maps)
After this, multiply the clip's "ss" and "len" in the timeline by the same stretch.
"""
import sys, os, json, glob, shutil, subprocess

sys.path.insert(0, os.path.dirname(__file__))
FPS = int(os.environ.get("FPS", 30))   # output frame rate (set FPS=60 for 60 fps episodes)
MI = "minterpolate=fps={f}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,setpts={s}*PTS,fps={o}"


def scale_times(cfg, s):
    """overlay timing given in seconds must stretch too"""
    for k in cfg.get("kinetic", []):
        k["start"] *= s; k["hold"] = k.get("hold", 1.2) * s
    for c in cfg.get("callouts", []):
        c["start"] *= s; c["end"] *= s
    return cfg


def retime_labels(src_json, n_src, fps_src, n_out, s, out_json):
    lab = json.load(open(src_json)); out = {}
    for j in range(n_out):
        fs = (j / FPS) / s * fps_src + 1           # fractional source frame (labels are 1-based)
        a = min(n_src, max(1, int(fs))); b = min(n_src, a + 1); w = min(1.0, max(0.0, fs - a))
        A, B = lab.get(str(a), {}), lab.get(str(b), {})
        fr = {}
        for name, va in A.items():
            vb = B.get(name, va)
            fr[name] = [x * (1 - w) + y * w for x, y in zip(va, vb)]
        out[str(j + 1)] = fr
    json.dump(out, open(out_json, "w"))


def overlay_mode(cfg_path, s, out_mp4):
    cfg = json.load(open(cfg_path))
    src, fps_src = cfg["frames_dir"], cfg.get("fps_in", 24)
    n_src = len(glob.glob(os.path.join(src, "f[0-9][0-9][0-9][0-9].png")))
    dst = src.rstrip("/") + f"_x{s:g}"
    shutil.rmtree(dst, ignore_errors=True); os.makedirs(dst)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps_src), "-i", f"{src}/f%04d.png",
                    "-vf", MI.format(f=round(FPS * s, 3), s=s, o=FPS), "-start_number", "1", f"{dst}/f%04d.png"], check=True)
    n_out = len(glob.glob(f"{dst}/f*.png"))
    if cfg.get("labels_json"):
        lj = os.path.join(dst, "labels.json")
        retime_labels(cfg["labels_json"], n_src, fps_src, n_out, s, lj); cfg["labels_json"] = lj
    cfg.update(frames_dir=dst, fps_in=FPS, fps_out=FPS, out_mp4=out_mp4)
    import overlay
    overlay.run_config(scale_times(cfg, s))
    shutil.rmtree(out_mp4 + ".frames", ignore_errors=True); shutil.rmtree(dst, ignore_errors=True)
    print("smooth ok", out_mp4, n_src, "->", n_out, "frames")


def video_mode(src, s, out_mp4):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-vf", MI.format(f=round(FPS * s, 3), s=s, o=FPS),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", out_mp4], check=True)
    print("smooth ok", out_mp4)


if __name__ == "__main__":
    mode, path, s, out = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]
    (overlay_mode if mode == "overlay" else video_mode)(path, s, out)
