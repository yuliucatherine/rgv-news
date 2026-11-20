"""Animated 2D water maps (1920x1080, 60 fps) from Census TIGER data (public domain):
the Rio Grande glows and 'flows' downstream, reservoirs pulse, irrigation canals draw themselves
outward, towns pop in, and the view keeps moving along keyframed boxes.
Usage: python3 pipeline/water_map.py <config.json> <out.mp4>
config: {"seconds": 13, "fps": 60, "counties": ["48465", ...],      # TIGER county FIPS for water layers
         "views": [[t, lon0, lat0, lon1, lat1], ...],                # camera keyframes (t in 0..1)
         "river_flow": [0.1, 0.6],                                    # river reveals west->east in this window
         "canals": [0.3, 0.8] or null, "canal_counties": [...],
         "reservoirs": ["Amistad", "Falcon"], "towns": [[name, lat, lon, appear_t], ...],
         "labels": [[text, lat, lon, appear_t, size, color], ...], "note": "..."}
"""
import sys, os, json, math, shutil, subprocess
import numpy as np, pandas as pd, geopandas as gpd
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pyproj import Transformer

W, H = 1920, 1080
FD = "/usr/share/fonts/opentype/inter"
NAVY = (9, 16, 32); LAND = (17, 27, 48); INK = (241, 245, 249); SUB = (148, 163, 184)
RIVER = (56, 189, 248); RES = (45, 212, 191); CANAL = (125, 211, 252); ORANGE = (249, 115, 22)
TO3857 = Transformer.from_crs(4326, 3857, always_xy=True)
def F(w, s): return ImageFont.truetype(f"{FD}/Inter-{w}.otf", s)
def ease(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)


def merc(lon, lat): return TO3857.transform(lon, lat)


def box(lon0, lat0, lon1, lat1):
    (x0, y0), (x1, y1) = merc(lon0, lat0), merc(lon1, lat1)
    cx, cy, w, h = (x0 + x1) / 2, (y0 + y1) / 2, abs(x1 - x0), abs(y1 - y0)
    if w / h > W / H: h = w * H / W
    else: w = h * W / H
    return np.array([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2])


def interp(a, b, t):
    ca, cb = (a[:2] + a[2:]) / 2, (b[:2] + b[2:]) / 2
    w = math.exp(math.log(a[2] - a[0]) * (1 - t) + math.log(b[2] - b[0]) * t); c = ca * (1 - t) + cb * t; h = w * H / W
    return np.array([c[0] - w / 2, c[1] - h / 2, c[0] + w / 2, c[1] + h / 2])


def view_at(views, t):
    for (ta, *ba), (tb, *bb) in zip(views, views[1:]):
        if t <= tb: return interp(box(*ba), box(*bb), ease((t - ta) / max(1e-6, tb - ta)))
    return box(*views[-1][1:])


def px(xs, ys, bb): return (np.asarray(xs) - bb[0]) / (bb[2] - bb[0]) * W, (bb[3] - np.asarray(ys)) / (bb[3] - bb[1]) * H


def draw(d, geom, bb, fill=None, outline=None, width=2):
    for p in getattr(geom, "geoms", [geom]):
        if p.geom_type == "Polygon":
            xs, ys = p.exterior.xy; X, Y = px(xs, ys, bb); pts = list(zip(X, Y))
            if len(pts) > 2:
                if fill: d.polygon(pts, fill=fill)
                if outline: d.line(pts, fill=outline, width=width)
        elif p.geom_type in ("LineString", "LinearRing"):
            xs, ys = p.xy; X, Y = px(xs, ys, bb); pts = list(zip(X, Y))
            if len(pts) > 1: d.line(pts, fill=outline or fill, width=width, joint="curve")
        elif hasattr(p, "geoms"):
            draw(d, p, bb, fill, outline, width)


def main(cfg, out):
    g = "data/geo/"
    fps = cfg.get("fps", 60); n = int(cfg.get("seconds", 12) * fps)
    st = gpd.read_file(g + "cb_2023_us_state_500k.zip").to_crs(3857)
    tx = st[st.STUSPS == "TX"].geometry.iloc[0].simplify(800)
    nb = st[st.STUSPS.isin(["NM", "OK", "AR", "LA"])].geometry.simplify(2000)
    co = gpd.read_file(g + "cb_2023_us_county_500k.zip"); co = co[co.STATEFP == "48"].to_crs(3857).geometry.simplify(300)
    aw = pd.concat([gpd.read_file(f"{g}tl_2023_{c}_areawater.zip") for c in cfg["counties"]]).to_crs(3857)
    names = aw.FULLNAME.fillna("")
    river = aw[names.str.contains("Rio Grande|Río Grande")].geometry.simplify(40)
    res = {r: aw[names.str.contains(r)].geometry.simplify(40) for r in cfg.get("reservoirs", [])}
    lw = None
    if cfg.get("canals"):
        lw = pd.concat([gpd.read_file(f"{g}tl_2023_{c}_linearwater.zip") for c in cfg.get("canal_counties", cfg["counties"])]).to_crs(3857)
        lw = lw[lw.MTFCC == "H3020"]
        lw["cy"] = lw.geometry.centroid.y; lw = lw.sort_values("cy")      # draw south (river) -> north
        canal_geoms = list(lw.geometry.simplify(20))
    # river reveal by longitude (west -> east)
    rb = river.total_bounds if len(river) else [0, 0, 1, 1]
    views = cfg["views"]; r0, r1 = cfg.get("river_flow", [0.05, 0.5])
    tmp = out + ".frames"; shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
    towns = [(nm, *merc(lon, lat), ta) for nm, lat, lon, ta in cfg.get("towns", [])]
    labels = [(l[0], *merc(l[2], l[1]), l[3], l[4], tuple(l[5]), l[6] if len(l) > 6 else 9.0)   # optional 7th: hide time
              for l in cfg.get("labels", [])]
    for f in range(n):
        t = f / max(1, n - 1); bb = view_at(views, t)
        fr = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(fr, "RGBA")
        draw(d, tx, bb, fill=LAND, outline=(148, 163, 184, 220), width=3)
        for gg in nb: draw(d, gg, bb, outline=(71, 85, 105, 160), width=2)
        for gg in co: draw(d, gg, bb, outline=(51, 65, 85, 110), width=1)
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dg = ImageDraw.Draw(glow)
        # river flowing west -> east
        k = ease((t - r0) / max(1e-6, r1 - r0)); xcut = rb[0] + (rb[2] - rb[0]) * k
        for gg in river:
            if gg.bounds[0] <= xcut:
                draw(dg, gg, bb, fill=RIVER + (255,), outline=RIVER + (255,), width=4)
        # reservoirs pulse once the river reaches them
        for name, geoms in res.items():
            if not len(geoms): continue
            rx = geoms.total_bounds[0]
            if rx > xcut: continue
            pulse = 0.75 + 0.25 * math.sin(f / fps * 3.0)
            for gg in geoms: draw(dg, gg, bb, fill=RES + (int(255 * pulse),), outline=RES + (255,), width=3)
        if lw is not None:
            c0, c1 = cfg["canals"]; kc = ease((t - c0) / max(1e-6, c1 - c0)); m = int(len(canal_geoms) * kc)
            for gg in canal_geoms[:m]: draw(dg, gg, bb, outline=CANAL + (230,), width=2)
        blur = glow.filter(ImageFilter.GaussianBlur(6))
        fr = fr.convert("RGBA"); fr.alpha_composite(blur); fr.alpha_composite(glow)
        tl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dt = ImageDraw.Draw(tl)
        for name, x, y, ta in towns:
            a = ease((t - ta) / 0.05)
            if a <= 0: continue
            X, Y = px([x], [y], bb); X, Y = float(X[0]), float(Y[0])
            if not (-50 < X < W + 50 and -50 < Y < H + 50): continue
            dt.ellipse([X - 8, Y - 8, X + 8, Y + 8], fill=(255, 255, 255, int(255 * a)), outline=NAVY + (int(255 * a),), width=3)
            dt.text((X + 14, Y - 18), name, font=F("Bold", 30), fill=(255, 255, 255, int(255 * a)),
                    stroke_width=4, stroke_fill=NAVY + (int(220 * a),))
        for txt, x, y, ta, sz, col, tb in labels:
            a = min(ease((t - ta) / 0.05), ease((tb - t) / 0.05))
            if a <= 0: continue
            X, Y = px([x], [y], bb)
            dt.text((float(X[0]), float(Y[0])), txt, font=F("Black", sz), fill=col + (int(255 * a),), anchor="mm",
                    stroke_width=5, stroke_fill=NAVY + (int(220 * a),))
        if cfg.get("note"):
            dt.text((W - 40, H - 40), cfg["note"], font=F("Medium", 22), fill=(203, 213, 225, 220), anchor="rs")
        fr.alpha_composite(tl)
        fr.convert("RGB").save(f"{tmp}/{f:05d}.png")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", f"{tmp}/%05d.png",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", out], check=True)
    shutil.rmtree(tmp); print("water map ok", out)


if __name__ == "__main__":
    main(json.load(open(sys.argv[1])), sys.argv[2])
