"""Animated zoom map: Texas -> Lower Rio Grande Valley, drawn frame by frame.
Data: U.S. Census Bureau cartographic boundaries + TIGER (public domain);
imagery: USGS The National Map, USGSImageryOnly (public domain).
Usage: python3 map_anim.py <data_dir> <out.mp4> [seconds]
"""
import sys, os, math, io, subprocess, urllib.request
import numpy as np, pandas as pd, geopandas as gpd
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1920, 1080, 30
FD = "/usr/share/fonts/opentype/inter"
NAVY = (9, 16, 32); INK = (241, 245, 249); MUTED = (148, 163, 184)
ORANGE = (249, 115, 22); WATER = (56, 189, 248); ROAD = (226, 232, 240)
RGV = ["Starr", "Hidalgo", "Cameron", "Willacy"]
CITIES = [("McAllen", 26.2034, -98.2300), ("Edinburg", 26.3017, -98.1633),
          ("Harlingen", 26.1906, -97.6961), ("Brownsville", 25.9017, -97.4975),
          ("Rio Grande City", 26.3798, -98.8203)]


def F(w, s): return ImageFont.truetype(f"{FD}/Inter-{w}.otf", s)


def ease(t): return t * t * (3 - 2 * t)


def load(d):
    g = f"{d}/geo/"
    st = gpd.read_file(g + "cb_2023_us_state_500k.zip").to_crs(3857)
    co = gpd.read_file(g + "cb_2023_us_county_500k.zip")
    co = co[co.STATEFP == "48"].to_crs(3857)
    w = pd.concat([gpd.read_file(f"{g}tl_2023_{c}_areawater.zip")
                   for c in ["48215", "48061", "48427", "48489", "48505"]]).to_crs(3857)
    r = gpd.read_file(g + "tl_2023_48_prisecroads.zip").to_crs(3857)
    roads = r[r.FULLNAME.fillna("").str.match(r"^(I- 2|I- 69 ?[CE]?|US Hwy 83|US Hwy 77|US Hwy 281)\b")]
    return st, co, w, roads


def usgs(bbox, size):
    x0, y0, x1, y1 = bbox
    url = ("https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/export"
           f"?bbox={x0},{y0},{x1},{y1}&bboxSR=3857&imageSR=3857&size={size[0]},{size[1]}&format=jpg&f=image")
    return Image.open(io.BytesIO(urllib.request.urlopen(url, timeout=60).read())).convert("RGB")


def fit_bbox(geom_bounds, pad=0.08):
    x0, y0, x1, y1 = geom_bounds
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    w, h = (x1 - x0) * (1 + pad), (y1 - y0) * (1 + pad)
    if w / h > W / H: h = w * H / W
    else: w = h * W / H
    return np.array([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2])


def interp_bbox(a, b, t):
    # zoom in log-space on width, linear on center, for a smooth "fly-in"
    ca, cb = (a[:2] + a[2:]) / 2, (b[:2] + b[2:]) / 2
    wa, wb = a[2] - a[0], b[2] - b[0]
    w = math.exp(math.log(wa) * (1 - t) + math.log(wb) * t)
    c = ca * (1 - t) + cb * t
    h = w * H / W
    return np.array([c[0] - w / 2, c[1] - h / 2, c[0] + w / 2, c[1] + h / 2])


def to_px(xs, ys, bb):
    return (xs - bb[0]) / (bb[2] - bb[0]) * W, (bb[3] - ys) / (bb[3] - bb[1]) * H


def draw_geom(d, geom, bb, **kw):
    polys = getattr(geom, "geoms", [geom])
    for p in polys:
        rings = [p.exterior] + list(p.interiors) if p.geom_type == "Polygon" else [p]
        for i, ring in enumerate(rings):
            xs, ys = np.asarray(ring.xy)
            px, py = to_px(xs, ys, bb)
            pts = list(zip(px, py))
            if len(pts) < 2: continue
            if p.geom_type == "Polygon" and "fill" in kw and i == 0:
                d.polygon(pts, fill=kw["fill"])
            if "outline" in kw:
                d.line(pts, fill=kw["outline"], width=kw.get("width", 2), joint="curve")


def main(data_dir, out, seconds=8.0):
    st, co, water, roads = load(data_dir)
    texas = st[st.STUSPS == "TX"]
    rgv = co[co.NAME.isin(RGV)]
    b_tx = fit_bbox(texas.total_bounds, 0.12)
    b_rgv = fit_bbox(rgv.total_bounds, 0.18)
    river = water[water.FULLNAME.fillna("").str.contains("Río Grande|Rio Grande|Falcon")]
    canals = water[water.FULLNAME.fillna("").str.contains("Cnl|Canal")]
    # simplify for speed at each scale
    tx_s = texas.geometry.simplify(2000).iloc[0]
    nb = st[st.STUSPS.isin(["NM", "OK", "AR", "LA"])].geometry.simplify(3000)
    co_s = co.geometry.simplify(500)
    rgv_s = rgv.geometry.simplify(150)
    img = usgs(b_rgv, (2400, 1350)).resize((W, H), Image.LANCZOS)
    img = Image.blend(img, Image.new("RGB", (W, H), NAVY), 0.18)
    # USGS imagery covers the U.S. only: mask it to Texas so the edge follows the Rio Grande
    mask = Image.new("L", (W, H), 0)
    draw_geom(ImageDraw.Draw(mask), texas.geometry.iloc[0], b_rgv, fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(1.5))
    img = Image.composite(img, Image.new("RGB", (W, H), (14, 22, 40)), mask)

    tmp = out + ".frames"; os.makedirs(tmp, exist_ok=True)
    n = int(seconds * FPS)
    zoom_end = 0.62  # fraction of time spent zooming
    fname = F("Black", 44); fcity = F("Bold", 30); fsrc = F("Medium", 22); fk = F("Black", 30)
    for i in range(n):
        t = i / (n - 1)
        z = ease(min(1, t / zoom_end))
        bb = interp_bbox(b_tx, b_rgv, z)
        frame = Image.new("RGB", (W, H), NAVY)
        # imagery fades in during the last part of the zoom
        a = max(0.0, min(1.0, (z - 0.55) / 0.4))
        if a > 0:
            # crop the final-extent imagery to the current view (only valid near the end)
            sx = (bb[0] - b_rgv[0]) / (b_rgv[2] - b_rgv[0]) * W
            sy = (b_rgv[3] - bb[3]) / (b_rgv[3] - b_rgv[1]) * H
            sw = (bb[2] - bb[0]) / (b_rgv[2] - b_rgv[0]) * W
            crop = img.transform((W, H), Image.EXTENT, (sx, sy, sx + sw, sy + sw * H / W), Image.BILINEAR)
            frame = Image.blend(frame, crop, a)
        d = ImageDraw.Draw(frame, "RGBA")
        for g in nb: draw_geom(d, g, bb, outline=(71, 85, 105, 160), width=2)
        for g in co_s: draw_geom(d, g, bb, outline=(100, 116, 139, int(110 * (1 - a) + 40)), width=1)
        draw_geom(d, tx_s, bb, outline=(203, 213, 225, 230), width=3)
        # RGV counties pulse in after the zoom starts
        h = max(0.0, min(1.0, (t - 0.15) / 0.3))
        for g in rgv_s:
            draw_geom(d, g, bb, fill=(249, 115, 22, int(70 * h * (1 - 0.75 * a))), outline=(249, 115, 22, int(255 * h)), width=4)
        if z > 0.5:
            wa = min(1, (z - 0.5) / 0.3)
            for g in river.geometry: draw_geom(d, g, bb, fill=(56, 189, 248, int(220 * wa)), outline=(56, 189, 248, int(255 * wa)), width=3)
        if t > zoom_end:
            k = min(1, (t - zoom_end) / 0.15)
            for g in canals.geometry: draw_geom(d, g, bb, fill=(125, 211, 252, int(200 * k)))
            for g in roads.geometry: draw_geom(d, g, bb, outline=(226, 232, 240, int(170 * k)), width=3)
            for name, lat, lon in CITIES:
                from pyproj import Transformer
                x, y = Transformer.from_crs(4326, 3857, always_xy=True).transform(lon, lat)
                px, py = to_px(np.array([x]), np.array([y]), bb)
                px, py = float(px[0]), float(py[0])
                d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=(255, 255, 255, int(255 * k)), outline=NAVY + (int(255 * k),), width=3)
                d.text((px + 14, py - 18), name, font=fcity, fill=(255, 255, 255, int(255 * k)),
                       stroke_width=4, stroke_fill=NAVY + (int(200 * k),))
        # top scrim for the title, MEXICO label, then title card + source line
        for yy in range(0, 230, 2):
            d.rectangle([0, yy, W, yy + 2], fill=NAVY + (int(200 * (1 - yy / 230) ** 1.5),))
        if a > 0.5:
            d.text((560, 1000), "MEXICO", font=F("Bold", 34), fill=(148, 163, 184, int(180 * a)))
        ta = min(1, t / 0.08)
        d.rounded_rectangle([64, 60, 64 + 14, 60 + 52], 3, fill=ORANGE + (int(255 * ta),))
        title = "TEXAS" if z < 0.45 else "THE LOWER RIO GRANDE VALLEY"
        d.text((96, 58), title, font=fname, fill=(241, 245, 249, int(255 * ta)))
        if z >= 0.45:
            d.text((96, 112), "Starr · Hidalgo · Cameron · Willacy counties", font=F("SemiBold", 30), fill=(203, 213, 225, int(255 * ta)))
        src = "Map: U.S. Census Bureau (TIGER)" + (" · Imagery: USGS The National Map" if a > 0 else "")
        d.text((W - 40, H - 40), src, font=fsrc, fill=(203, 213, 225, 220), anchor="rs")
        frame.save(f"{tmp}/{i:04d}.png")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{tmp}/%04d.png",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", out], check=True)
    print("map ok", out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 8.0)
