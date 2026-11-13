"""Fetch a heightmap (AWS Terrain Tiles, terrarium encoding) and a matching USGS imagery
texture for a lon/lat box, in Web Mercator. Writes height.npy, texture.jpg, meta.json.
Usage: python3 terrain_fetch.py <out_dir> lon0 lat0 lon1 lat1 [zoom]
Elevation: Mapzen/AWS Terrain Tiles (derived from SRTM, USGS 3DEP and others; open data).
Imagery: USGS The National Map, USGSImageryOnly (public domain, U.S. only).
"""
import sys, os, io, json, math, urllib.request
import numpy as np
from PIL import Image
from pyproj import Transformer

UA = {"User-Agent": "rgv-news-video-pipeline/1.0"}


def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()


def tile_xy(lon, lat, z):
    n = 2 ** z
    x = (lon + 180) / 360 * n
    y = (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n
    return x, y


def main(out, lon0, lat0, lon1, lat1, z=12):
    os.makedirs(out, exist_ok=True)
    x0, y1 = tile_xy(lon0, lat0, z); x1, y0 = tile_xy(lon1, lat1, z)
    tx0, tx1, ty0, ty1 = int(x0), int(x1), int(y0), int(y1)
    mosaic = np.zeros(((ty1 - ty0 + 1) * 256, (tx1 - tx0 + 1) * 256), np.float32)
    for tx in range(tx0, tx1 + 1):
        for ty in range(ty0, ty1 + 1):
            im = np.asarray(Image.open(io.BytesIO(get(
                f"https://elevation-tiles-prod.s3.amazonaws.com/terrarium/{z}/{tx}/{ty}.png"))).convert("RGB"), np.float32)
            e = im[..., 0] * 256 + im[..., 1] + im[..., 2] / 256 - 32768
            mosaic[(ty - ty0) * 256:(ty - ty0 + 1) * 256, (tx - tx0) * 256:(tx - tx0 + 1) * 256] = e
    # crop to the exact box
    px0, px1 = int((x0 - tx0) * 256), int((x1 - tx0) * 256)
    py0, py1 = int((y0 - ty0) * 256), int((y1 - ty0) * 256)
    h = mosaic[py0:py1, px0:px1]
    np.save(f"{out}/height.npy", h)
    tr = Transformer.from_crs(4326, 3857, always_xy=True)
    mx0, my0 = tr.transform(lon0, lat0); mx1, my1 = tr.transform(lon1, lat1)
    w = 2048; hh = int(w * (my1 - my0) / (mx1 - mx0))
    url = ("https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/export"
           f"?bbox={mx0},{my0},{mx1},{my1}&bboxSR=3857&imageSR=3857&size={w},{hh}&format=jpg&f=image")
    Image.open(io.BytesIO(get(url))).convert("RGB").save(f"{out}/texture.jpg", quality=92)
    meta = dict(lon0=lon0, lat0=lat0, lon1=lon1, lat1=lat1, zoom=z, width_m=mx1 - mx0,
                height_m=my1 - my0, shape=list(h.shape), emin=float(h.min()), emax=float(h.max()))
    json.dump(meta, open(f"{out}/meta.json", "w"), indent=1)
    print(meta)


if __name__ == "__main__":
    a = sys.argv
    main(a[1], *map(float, a[2:6]), *(int(v) for v in a[6:7]))
