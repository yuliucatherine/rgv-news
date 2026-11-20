"""Animated line chart (1920x1080, 60 fps): glowing lines draw themselves left to right with a
leading dot and a live value tag, key points pop in with callouts as the line reaches them,
and the whole chart slowly pushes in, so there is always movement.
Usage: python3 pipeline/line_chart.py <config.json> <out.mp4>
config: {"seconds": 12, "fps": 60, "x": [1990, 2027], "y": [0, 100], "y_suffix": "%",
         "x_ticks": [1990, 2000, ...], "y_ticks": [0, 25, 50, 75, 100], "reveal": [0.05, 0.8],
         "series": [{"name": "Falcon", "color": [56,189,248], "csv": "falcon.csv", "col": "percent_full",
                     "from": "1990-01-01", "every": 7}  or  {"points": [[x, y], ...]}],
         "callouts": [{"series": 0, "x": 2010.8, "text": "100% full", "sub": "Oct 2010", "dy": -70}],
         "note": "Source: ...", "label_lines": true}
x values for CSV series are decimal years.
"""
import sys, os, json, csv, math, shutil, subprocess, datetime as dt
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1920, 1080
FD = "/usr/share/fonts/opentype/inter"
NAVY = (9, 16, 32); INK = (241, 245, 249); SUB = (148, 163, 184); GRID = (30, 41, 66); ORANGE = (249, 115, 22)
def F(w, s): return ImageFont.truetype(f"{FD}/Inter-{w}.otf", s)
def ease(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
def back(t):
    t = max(0.0, min(1.0, t)); c = 1.6; return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2


def load_series(s):
    if "points" in s: return np.array(s["points"], float)
    rows = [r for r in csv.DictReader(l for l in open(s["csv"]) if not l.startswith("#")) if r.get(s["col"])]
    rows = [r for r in rows if r["date"] >= s.get("from", "0000")]
    pts = []
    for i, r in enumerate(rows):
        if i % s.get("every", 1) and i != len(rows) - 1: continue
        d = dt.date.fromisoformat(r["date"]); x = d.year + (d.timetuple().tm_yday - 1) / 365.25
        pts.append((x, float(r[s["col"]])))
    return np.array(pts)


def main(cfg, out):
    fps = cfg.get("fps", 60); n = int(cfg.get("seconds", 10) * fps)
    x0, x1 = cfg["x"]; y0, y1 = cfg["y"]; suf = cfg.get("y_suffix", ""); pre = cfg.get("y_prefix", "")
    L, R, T, B = 170, 1700, 250, 900       # plot box (leaves room for the episode headline + captions)
    px = lambda x: L + (x - x0) / (x1 - x0) * (R - L)
    py = lambda y: B - (y - y0) / (y1 - y0) * (B - T)
    series = [(s, load_series(s)) for s in cfg["series"]]
    r0, r1 = cfg.get("reveal", [0.05, 0.8])
    # static background
    bg = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(bg)
    for yt in cfg.get("y_ticks", []):
        d.line([(L, py(yt)), (R, py(yt))], fill=GRID, width=2)
        d.text((L - 20, py(yt)), f"{pre}{yt:,}{suf}", font=F("Medium", 28), fill=SUB, anchor="rm")
    for xt in cfg.get("x_ticks", []):
        d.line([(px(xt), B), (px(xt), B + 12)], fill=SUB, width=2)
        d.text((px(xt), B + 22), str(xt), font=F("Medium", 28), fill=SUB, anchor="ma")
    d.line([(L, B), (R, B)], fill=SUB, width=3)
    if cfg.get("note"):
        d.text((W - 40, H - 40), cfg["note"], font=F("Medium", 22), fill=(203, 213, 225), anchor="rs")
    tmp = out + ".frames"; shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
    callouts = cfg.get("callouts", [])
    for f in range(n):
        t = f / max(1, n - 1)
        prog = ease((t - r0) / (r1 - r0)); xr = x0 + (x1 - x0) * prog
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
        heads = []
        for (s, pts) in series:
            col = tuple(s.get("color", [56, 189, 248]))
            vis = pts[pts[:, 0] <= xr]
            if len(vis) >= 2:
                xy = [(px(a), py(b)) for a, b in vis]
                # area fill under the line
                poly = xy + [(xy[-1][0], B), (xy[0][0], B)]
                dl.polygon(poly, fill=col + (38,))
                dl.line(xy, fill=col + (255,), width=6, joint="curve")
                heads.append((s, col, xy[-1], vis[-1][1]))
        glow = lay.filter(ImageFilter.GaussianBlur(10))
        fr = bg.copy().convert("RGBA"); fr.alpha_composite(glow); fr.alpha_composite(lay)
        d2 = ImageDraw.Draw(fr)
        for s, col, (hx, hy), val in heads:
            if prog < 0.999 or cfg.get("keep_head", True):
                d2.ellipse([hx - 11, hy - 11, hx + 11, hy + 11], fill=col + (255,), outline=(255, 255, 255, 255), width=3)
                if cfg.get("label_lines", True):
                    tag = f"{s['name']}  {pre}{val:,.{cfg.get('y_dec', 0)}f}{suf}"
                    tw = d2.textlength(tag, font=F("Bold", 30))
                    tx = min(hx + 24, W - tw - 30)
                    d2.rounded_rectangle([tx - 10, hy - 26, tx + tw + 12, hy + 22], 8, fill=NAVY + (220,))
                    d2.text((tx, hy), tag, font=F("Bold", 30), fill=INK + (255,), anchor="lm")
        for c in callouts:
            s, pts = series[c.get("series", 0)]
            if xr < c["x"]: continue
            k = (xr - c["x"]) / ((x1 - x0) * 0.04 + 1e-9); a = ease(k); p = back(k)
            i = int(np.argmin(np.abs(pts[:, 0] - c["x"]))); cx, cy = px(pts[i, 0]), py(pts[i, 1])
            dy = c.get("dy", -80); ly = cy + dy * p
            d2.line([(cx, cy), (cx, ly)], fill=(255, 255, 255, int(200 * a)), width=2)
            d2.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=ORANGE + (int(255 * a),), outline=(255, 255, 255, int(255 * a)), width=3)
            f1, f2 = F("Black", 40), F("SemiBold", 26)
            tw = max(d2.textlength(c["text"], font=f1), d2.textlength(c.get("sub", ""), font=f2))
            bx = min(max(cx - tw / 2, L), R - tw); by = ly - (78 if dy < 0 else -10)
            d2.rounded_rectangle([bx - 16, by - 8, bx + tw + 16, by + 76], 10, fill=NAVY + (int(230 * a),),
                                 outline=ORANGE + (int(255 * a),), width=2)
            d2.text((bx, by), c["text"], font=f1, fill=INK + (int(255 * a),))
            if c.get("sub"): d2.text((bx, by + 46), c["sub"], font=f2, fill=SUB + (int(255 * a),))
        # slow push-in toward the right side of the chart (movement even when lines are done)
        z = 1 + 0.045 * ease(t)
        zw, zh = int(W * z), int(H * z)
        ox = int((zw - W) * 0.7); oy = int((zh - H) * 0.5)
        fr = fr.convert("RGB").resize((zw, zh), Image.BICUBIC).crop((ox, oy, ox + W, oy + H))
        fr.save(f"{tmp}/{f:05d}.png")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", f"{tmp}/%05d.png",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", out], check=True)
    shutil.rmtree(tmp); print("chart ok", out)


if __name__ == "__main__":
    main(json.load(open(sys.argv[1])), sys.argv[2])
