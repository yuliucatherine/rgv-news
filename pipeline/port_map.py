"""Animated 2D local map (1920x1080, 60 fps) from Census TIGER data (public domain): water bodies,
a highlighted channel that draws itself in, a highlighted road, pulsing site markers and labels,
with the camera always moving between keyframed boxes.
Usage: python3 pipeline/port_map.py <config.json> <out.mp4>
config: {"seconds": 20, "county": "48061", "views": [[t, lon0, lat0, lon1, lat1], ...],
         "water_glow": [["Brownsville Ship", [0.05, 0.3]]],      # areawater name match + reveal window
         "road": ["State Hwy 48", [0.3, 0.5]] or null,
         "sites": [[name, lat, lon, appear_t, "orange"|"white"], ...],
         "labels": [[text, lat, lon, appear_t, size], ...], "note": "..."}
"""
import sys, os, json, math, shutil, subprocess
import geopandas as gpd
from shapely.geometry import Polygon
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from water_map import W, H, F, ease, merc, px, draw, view_at, NAVY, LAND, RIVER, ORANGE

WATER = (30, 64, 110)


def main(cfg, out):
    g = "data/geo/"; fps = cfg.get("fps", 60); n = int(cfg.get("seconds", 20) * fps); c = cfg.get("county", "48061")
    st = gpd.read_file(g + "tl_2023_us_state.zip")
    tx4 = st[st.STUSPS == "TX"].geometry.iloc[0]
    mex = None
    if cfg.get("mexico_coast"):   # land south of the river: box west of an approximate Mexican coastline, minus Texas
        cst = cfg["mexico_coast"]; poly = Polygon([(-99, 25.0), (cst[-1][0], 25.0)] + cst[::-1] + [(cst[0][0], 26.3), (-99, 26.3)])
        mex = gpd.GeoSeries([poly.difference(tx4)], crs=4269).to_crs(3857).simplify(30).iloc[0]
    tx = gpd.GeoSeries([tx4], crs=4269).to_crs(3857).simplify(15).iloc[0]
    aw = gpd.read_file(f"{g}tl_2023_{c}_areawater.zip").to_crs(3857); names = aw.FULLNAME.fillna("")
    water = list(aw.geometry.simplify(15))
    river = aw[names.str.contains("Rio Grande|Río Grande")].geometry.simplify(15)
    glows = []
    for match, (a, b) in cfg.get("water_glow", []):
        gs = aw[names.str.contains(match)].geometry.simplify(10)
        glows.append((list(gs), gs.total_bounds, a, b))
    road = None
    if cfg.get("road"):
        rd = gpd.read_file(f"{g}tl_2023_{c}_roads.zip"); rd = rd[rd.FULLNAME.fillna("") == cfg["road"][0]].to_crs(3857)
        road = (list(rd.geometry.simplify(10)), rd.total_bounds, *cfg["road"][1])
    sites = [(nm, *merc(lon, lat), ta, col) for nm, lat, lon, ta, col in cfg.get("sites", [])]
    labels = [(l[0], *merc(l[2], l[1]), l[3], l[4], tuple(l[5]) if len(l) > 5 else (253, 224, 71))
              for l in cfg.get("labels", [])]
    tmp = out + ".frames"; shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
    for f in range(n):
        t = f / max(1, n - 1); bb = view_at(cfg["views"], t); sec = f / fps
        fr = Image.new("RGB", (W, H), WATER); d = ImageDraw.Draw(fr, "RGBA")
        if mex is not None: draw(d, mex, bb, fill=(14, 22, 40))
        draw(d, tx, bb, fill=LAND)
        for gg in water: draw(d, gg, bb, fill=WATER + (255,))
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dg = ImageDraw.Draw(glow)
        for gg in river: draw(dg, gg, bb, fill=RIVER + (200,), outline=RIVER + (230,), width=3)
        for gs, tb, a, b in glows:      # reveal west -> east
            k = ease((t - a) / max(1e-6, b - a)); xcut = tb[0] + (tb[2] - tb[0]) * k
            for gg in gs:
                if k > 0 and gg.bounds[0] <= xcut: draw(dg, gg, bb, fill=ORANGE + (255,), outline=ORANGE + (255,), width=3)
        if road:
            rs, tb, a, b = road; k = ease((t - a) / max(1e-6, b - a)); xcut = tb[0] + (tb[2] - tb[0]) * k
            for gg in rs:
                if k > 0 and gg.bounds[0] <= xcut: draw(dg, gg, bb, outline=(253, 224, 71, 255), width=5)
        blur = glow.filter(ImageFilter.GaussianBlur(7))
        fr = fr.convert("RGBA"); fr.alpha_composite(blur); fr.alpha_composite(glow)
        tl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dt = ImageDraw.Draw(tl)
        for nm, x, y, ta, col in sites:
            a = ease((t - ta) / 0.04)
            if a <= 0: continue
            X, Y = px([x], [y], bb); X, Y = float(X[0]), float(Y[0])
            cc = ORANGE if col == "orange" else (255, 255, 255)
            ph = (sec * 0.9) % 1.0; rr = 10 + 46 * ph          # sonar ring keeps the frame alive
            dt.ellipse([X - rr, Y - rr, X + rr, Y + rr], outline=cc + (int(200 * a * (1 - ph)),), width=4)
            dt.ellipse([X - 10, Y - 10, X + 10, Y + 10], fill=cc + (int(255 * a),), outline=NAVY + (int(255 * a),), width=3)
            dt.text((X + 18, Y - 20), nm, font=F("Bold", 32), fill=(255, 255, 255, int(255 * a)),
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
    print("port map ok", out)


if __name__ == "__main__":
    main(json.load(open(sys.argv[1])), sys.argv[2])
