"""Fetch a high-resolution aerial photo (USGS The National Map, USGSImageryOnly, public domain) for a box
around a point, via the MapServer export endpoint (about 0.6 m/pixel in the Valley; cached tiles stop at z16).
Usage: python3 aerial_fetch.py <out.jpg> <lon> <lat> <width_m> [px_w=3840] [px_h=2160]
The box keeps the output aspect ratio. Credit on screen: "Imagery: USGS The National Map".
"""
import sys, math, urllib.request, urllib.parse

UA = {"User-Agent": "rgv-news-video-pipeline/1.0"}
out, lon, lat, wm = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
pw = int(sys.argv[5]) if len(sys.argv) > 5 else 3840
ph = int(sys.argv[6]) if len(sys.argv) > 6 else 2160
R = 6378137.0
x = math.radians(lon) * R; y = math.log(math.tan(math.pi / 4 + math.radians(lat) / 2)) * R
k = 1 / math.cos(math.radians(lat))          # Web Mercator stretch at this latitude
hw = wm / 2 * k; hh = hw * ph / pw
q = urllib.parse.urlencode({"bbox": f"{x - hw},{y - hh},{x + hw},{y + hh}", "bboxSR": 3857, "imageSR": 3857,
                            "size": f"{pw},{ph}", "format": "jpg", "f": "image"})
u = "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/export?" + q
open(out, "wb").write(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=120).read())
print("ok", out)
