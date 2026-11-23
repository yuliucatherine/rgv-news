"""Animated 2D highway map (1920x1080, 60 fps) from Census TIGER statewide primary/secondary roads (public domain):
named highways draw themselves in (solid or dashed), optional illustrative straight links (e.g. a proposed corridor),
pulsing site markers and labels, with the camera always moving between keyframed boxes.
Usage: python3 pipeline/route_map.py <config.json> <out.mp4>
config: {"seconds": 14, "fps": 60, "views": [[t, lon0, lat0, lon1, lat1], ...],
         "roads": [{"names": ["I- 69E"], "color": [45,212,191], "reveal": [0.1, 0.3], "axis": "y", "width": 7,
                    "dashed": false, "clip": [lon0, lat0, lon1, lat1] or null, "label": [text, lat, lon] or null}, ...],
         "links": [{"from": [lat, lon], "to": [lat, lon], "color": [...], "reveal": [a, b], "label": [text, lat, lon]}],
         "sites": [[name, lat, lon, appear_t, "orange"|"white"], ...],
         "labels": [[text, lat, lon, appear_t, size(, [r,g,b])], ...], "mexico_coast": [[lon, lat], ...], "note": "..."}
"""
import sys, os, json, math, shutil, subprocess
import geopandas as gpd
from shapely.geometry import Polygon, box as sbox, LineString
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from water_map import W, H, F, ease, merc, px, draw, view_at, NAVY, LAND, ORANGE

WATER = (30, 64, 110); GREY_ROAD = (71, 85, 105)


def dashed(d, pts, color, width, on=26, off=18):
    acc, draw_on = 0.0, True
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        seg = math.hypot(x1 - x0, y1 - y0); pos = 0.0
        while pos < seg:
            step = min((on if draw_on else off) - acc, seg - pos); a = pos / seg; b = (pos + step) / seg
            if draw_on: d.line([(x0 + (x1 - x0) * a, y0 + (y1 - y0) * a), (x0 + (x1 - x0) * b, y0 + (y1 - y0) * b)], fill=color, width=width)
            pos += step; acc += step
            if acc >= (on if draw_on else off) - 1e-6: acc, draw_on = 0.0, not draw_on


def lines_of(g):
    for p in getattr(g, "geoms", [g]):
        if p.geom_type == "LineString": yield p
        elif hasattr(p, "geoms"): yield from lines_of(p)


def main(cfg, out):
    g = "data/geo/"; fps = cfg.get("fps", 60); n = int(cfg.get("seconds", 14) * fps)
    st = gpd.read_file(g + "cb_2023_us_state_500k.zip")
    tx4 = st[st.STUSPS == "TX"].geometry.iloc[0]
    mex = None
    if cfg.get("mexico_coast"):
        cst = cfg["mexico_coast"]; poly = Polygon([(-101, 24.0), (cst[-1][0], 24.0)] + cst[::-1] + [(cst[0][0], 27.0), (-101, 30.0)])
        mex = gpd.GeoSeries([poly.difference(tx4)], crs=4269).to_crs(3857).simplify(200).iloc[0]
    tx = gpd.GeoSeries([tx4], crs=4269).to_crs(3857).simplify(150).iloc[0]
    co = gpd.read_file(g + "cb_2023_us_county_500k.zip"); co = co[co.STATEFP == "48"].to_crs(3857).geometry.simplify(150)
    rd = gpd.read_file(g + "tl_2023_48_prisecroads.zip"); names = rd.FULLNAME.fillna("")
    allv = cfg["views"]; lon0 = min(v[1] for v in allv) - 0.5; lat0 = min(v[2] for v in allv) - 0.5
    lon1 = max(v[3] for v in allv) + 0.5; lat1 = max(v[4] for v in allv) + 0.5
    near = rd[rd.intersects(sbox(lon0, lat0, lon1, lat1))]
    base = list(near[near.MTFCC == "S1100"].to_crs(3857).geometry.simplify(60))
    roads = []
    for r in cfg.get("roads", []):
        sel = rd[names.isin(r["names"])]
        if r.get("clip"): sel = sel.clip(sbox(*r["clip"]))
        sel = sel.to_crs(3857); geoms = [l for gg in sel.geometry.simplify(40) for l in lines_of(gg)]
        tb = sel.total_bounds
        lab = (r["label"][0], *merc(r["label"][2], r["label"][1])) if r.get("label") else None
        roads.append((geoms, tb, r))
        r["_lab"] = lab
    links = [(merc(l["from"][1], l["from"][0]), merc(l["to"][1], l["to"][0]), l) for l in cfg.get("links", [])]
    sites = [(nm, *merc(lon, lat), ta, col) for nm, lat, lon, ta, col in cfg.get("sites", [])]
    labels = [(l[0], *merc(l[2], l[1]), l[3], l[4], tuple(l[5]) if len(l) > 5 else (253, 224, 71)) for l in cfg.get("labels", [])]
    tmp = out + ".frames"; shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
    for f in range(n):
        t = f / max(1, n - 1); bb = view_at(cfg["views"], t); sec = f / fps
        fr = Image.new("RGB", (W, H), WATER); d = ImageDraw.Draw(fr, "RGBA")
        if mex is not None: draw(d, mex, bb, fill=(14, 22, 40))
        draw(d, tx, bb, fill=LAND)
        for c in co: draw(d, c, bb, outline=(51, 65, 85, 160), width=1)
        for gg in base: draw(d, gg, bb, outline=GREY_ROAD + (255,), width=3)
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dg = ImageDraw.Draw(glow)
        for geoms, tb, r in roads:
            a, b = r["reveal"]; k = ease((t - a) / max(1e-6, b - a))
            if k <= 0: continue
            col = tuple(r.get("color", [253, 224, 71])) + (255,); wd = r.get("width", 7); ax = r.get("axis", "x")
            cut = (tb[0] + (tb[2] - tb[0]) * k) if ax == "x" else (tb[1] + (tb[3] - tb[1]) * k)
            for ln in geoms:
                if ax == "x": keep = ln.intersection(sbox(tb[0] - 1, tb[1] - 1, cut, tb[3] + 1))
                else: keep = ln.intersection(sbox(tb[0] - 1, tb[1] - 1, tb[2] + 1, cut))
                for part in lines_of(keep):
                    X, Y = px(*part.xy, bb); pts = list(zip(X, Y))
                    if len(pts) < 2: continue
                    if r.get("dashed"): dashed(dg, pts, col, wd)
                    else: dg.line(pts, fill=col, width=wd, joint="curve")
        for (x0, y0), (x1, y1), l in links:
            a, b = l["reveal"]; k = ease((t - a) / max(1e-6, b - a))
            if k <= 0: continue
            X, Y = px([x0, x0 + (x1 - x0) * k], [y0, y0 + (y1 - y0) * k], bb)
            dashed(dg, list(zip(X, Y)), tuple(l.get("color", [249, 115, 22])) + (255,), l.get("width", 7))
        blur = glow.filter(ImageFilter.GaussianBlur(6))
        fr = fr.convert("RGBA"); fr.alpha_composite(blur); fr.alpha_composite(glow)
        tl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dt = ImageDraw.Draw(tl)
        items = [(r["_lab"], r["reveal"][1] - 0.03, tuple(r.get("color", [253, 224, 71]))) for _, _, r in roads if r["_lab"]]
        items += [((l["label"][0], *merc(l["label"][2], l["label"][1])), l["reveal"][1] - 0.03, tuple(l.get("color", [249, 115, 22])))
                  for _, _, l in links if l.get("label")]
        for (txt, x, y), ta, col in items:
            a = ease((t - ta) / 0.05)
            if a <= 0: continue
            X, Y = px([x], [y], bb)
            dt.text((float(X[0]), float(Y[0])), txt, font=F("Black", 34), fill=col + (int(255 * a),), anchor="mm",
                    stroke_width=6, stroke_fill=NAVY + (int(235 * a),))
        for nm, x, y, ta, col in sites:
            a = ease((t - ta) / 0.04)
            if a <= 0: continue
            X, Y = px([x], [y], bb); X, Y = float(X[0]), float(Y[0])
            cc = ORANGE if col == "orange" else (255, 255, 255)
            ph = (sec * 0.9) % 1.0; rr = 9 + 40 * ph
            dt.ellipse([X - rr, Y - rr, X + rr, Y + rr], outline=cc + (int(190 * a * (1 - ph)),), width=4)
            dt.ellipse([X - 9, Y - 9, X + 9, Y + 9], fill=cc + (int(255 * a),), outline=NAVY + (int(255 * a),), width=3)
            dt.text((X + 16, Y - 19), nm, font=F("Bold", 30), fill=(255, 255, 255, int(255 * a)),
                    stroke_width=5, stroke_fill=NAVY + (int(230 * a),))
        for txt, x, y, ta, sz, col in labels:
            a = ease((t - ta) / 0.04)
            if a <= 0: continue
            X, Y = px([x], [y], bb)
            dt.text((float(X[0]), float(Y[0])), txt, font=F("Black", sz), fill=col + (int(255 * a),), anchor="mm",
                    stroke_width=5, stroke_fill=NAVY + (int(230 * a),))
        if cfg.get("note"):
            dt.text((W - 40, H - 40), cfg["note"], font=F("Medium", 22), fill=(203, 213, 225, 220), anchor="rs")
        fr.alpha_composite(tl)
        fr.convert("RGB").save(f"{tmp}/{f:05d}.png")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", f"{tmp}/%05d.png",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", out], check=True)
    if not os.environ.get("KEEP"): shutil.rmtree(tmp)
    print("route map ok", out)


if __name__ == "__main__":
    main(json.load(open(sys.argv[1])), sys.argv[2])
