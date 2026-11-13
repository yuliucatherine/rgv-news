"""Blender (bpy) 3D terrain flyover from a heightmap made by terrain_fetch.py.
Stylized data-viz look: real elevation, brand-tinted terrain, animated water plane.
Writes PNG frames and labels.json (screen positions of named points per frame).
Usage: python3 terrain_shot.py <terrain_dir> <frames_dir> [seconds] [fps]
"""
import sys, os, json, math
import numpy as np
import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

tdir, fdir = sys.argv[1], sys.argv[2]
SECS = float(sys.argv[3]) if len(sys.argv) > 3 else 6
FPS = int(sys.argv[4]) if len(sys.argv) > 4 else 24
RES = (1280, 720)
SCALE = 100.0      # metres per Blender unit
VEX = 6.0          # vertical exaggeration
os.makedirs(fdir, exist_ok=True)
meta = json.load(open(f"{tdir}/meta.json"))
h = np.load(f"{tdir}/height.npy")[::2, ::2].astype(np.float64)   # downsample for CPU rendering
ny, nx = h.shape
# The elevation model stores the reservoir as a flat surface (Falcon: 91.7 m, conservation pool).
# Find it as the largest connected flat area at that level, then carve an ILLUSTRATIVE basin
# (depth grows with distance from shore) so a drawdown can be shown. Not real bathymetry.
from scipy import ndimage
POOL = float(os.environ.get("POOL_M", 91.7))
flat = np.abs(h - POOL) < 0.15
lab, n = ndimage.label(flat)
res = lab == (np.bincount(lab.ravel())[1:].argmax() + 1)
# Across the border the elevation source recorded the same reservoir at a different flat level
# (Falcon: ~97.0 m). Merge flat areas at that level that touch the main surface.
ALT = os.environ.get("ALT_POOL_M", "100.0")
if ALT:
    gy, gx = np.gradient(h)
    alt = (np.abs(h - float(ALT)) < 0.15) & (np.hypot(gx, gy) < 0.05)
    lab2, _ = ndimage.label(alt)
    touch = np.unique(lab2[ndimage.binary_dilation(res, iterations=4) & alt])
    res = res | np.isin(lab2, touch[touch > 0])
    res = ndimage.binary_closing(res, iterations=5)
res = ndimage.binary_fill_holes(res)
h = np.where(res, POOL, h)
# Coarse source data outside the U.S. is stepped into flat terraces; smooth those areas
gy, gx = np.gradient(h)
terr = ndimage.binary_dilation((np.hypot(gx, gy) < 0.02) & ~res, iterations=6)
hs = ndimage.gaussian_filter(h, 7)
h = np.where(terr & ~res, hs, ndimage.gaussian_filter(h, 0.8))
h = np.where(res, POOL, h)
dist = ndimage.distance_transform_edt(res)
depth = ndimage.gaussian_filter(22.0 * (1 - np.exp(-dist / 12.0)), 4) * res
h = np.where(res, h - depth, h)
water_cells = ndimage.binary_dilation(res, iterations=2)
W_bu, H_bu = meta["width_m"] / SCALE, meta["height_m"] / SCALE
base = float(np.percentile(h, 1))
z = (h - base) / SCALE * VEX


def lonlat_to_xy(lon, lat):
    # meta box is in Web Mercator; linear within such a small box is accurate enough for labels
    fx = (lon - meta["lon0"]) / (meta["lon1"] - meta["lon0"])
    def merc(la): return math.log(math.tan(math.pi / 4 + math.radians(la) / 2))
    fy = (merc(lat) - merc(meta["lat0"])) / (merc(meta["lat1"]) - merc(meta["lat0"]))
    return (fx - 0.5) * W_bu, (fy - 0.5) * H_bu


def height_at(x, y):
    i = int((0.5 - y / H_bu) * (ny - 1)); j = int((x / W_bu + 0.5) * (nx - 1))
    return float(z[min(max(i, 0), ny - 1), min(max(j, 0), nx - 1)])


bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene

# ---- terrain mesh straight from numpy ----
xs = np.linspace(-W_bu / 2, W_bu / 2, nx); ys = np.linspace(H_bu / 2, -H_bu / 2, ny)
X, Y = np.meshgrid(xs, ys)
verts = np.stack([X, Y, z], -1).reshape(-1, 3)
idx = np.arange(nx * ny).reshape(ny, nx)
quads = np.stack([idx[:-1, :-1], idx[1:, :-1], idx[1:, 1:], idx[:-1, 1:]], -1).reshape(-1, 4)
me = bpy.data.meshes.new("terrain")
me.vertices.add(len(verts)); me.vertices.foreach_set("co", verts.astype(np.float32).ravel())
me.loops.add(quads.size); me.loops.foreach_set("vertex_index", quads.ravel().astype(np.int32))
me.polygons.add(len(quads))
me.polygons.foreach_set("loop_start", (np.arange(len(quads)) * 4).astype(np.int32))
me.polygons.foreach_set("loop_total", np.full(len(quads), 4, np.int32))
me.update(); me.validate()
me.polygons.foreach_set("use_smooth", np.ones(len(quads), bool))
terrain = bpy.data.objects.new("terrain", me); sc.collection.objects.link(terrain)

# terrain material: elevation colour ramp (warm sand low -> slate high)
mat = bpy.data.materials.new("terrain"); mat.use_nodes = True
nt = mat.node_tree; bsdf = nt.nodes["Principled BSDF"]
geo = nt.nodes.new("ShaderNodeNewGeometry"); sep = nt.nodes.new("ShaderNodeSeparateXYZ")
mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["From Max"].default_value = float(z.max())
ramp = nt.nodes.new("ShaderNodeValToRGB"); cr = ramp.color_ramp
cr.elements[0].color = (0.42, 0.33, 0.24, 1); cr.elements[1].color = (0.20, 0.25, 0.33, 1)
e = cr.elements.new(0.45); e.color = (0.34, 0.33, 0.27, 1)
nt.links.new(geo.outputs["Position"], sep.inputs[0]); nt.links.new(sep.outputs["Z"], mr.inputs["Value"])
nt.links.new(mr.outputs["Result"], ramp.inputs["Fac"]); nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
bsdf.inputs["Roughness"].default_value = 0.9
terrain.data.materials.append(mat)

# ---- water plane: starts near full pool, draws down (illustrative) ----
dam_x, dam_y = lonlat_to_xy(-99.1683, 26.5575)
full = (POOL + 0.3 - base) / SCALE * VEX
low = (POOL - 15.0 - base) / SCALE * VEX
wq = quads[(water_cells[:-1, :-1] & water_cells[1:, 1:] & water_cells[1:, :-1] & water_cells[:-1, 1:]).ravel()]
used = np.unique(wq); remap = -np.ones(nx * ny, np.int64); remap[used] = np.arange(len(used))
wv = verts[used].copy(); wv[:, 2] = 0
wme = bpy.data.meshes.new("water")
wme.vertices.add(len(wv)); wme.vertices.foreach_set("co", wv.astype(np.float32).ravel())
wl = remap[wq]
wme.loops.add(wl.size); wme.loops.foreach_set("vertex_index", wl.ravel().astype(np.int32))
wme.polygons.add(len(wl)); wme.polygons.foreach_set("loop_start", (np.arange(len(wl)) * 4).astype(np.int32))
wme.polygons.foreach_set("loop_total", np.full(len(wl), 4, np.int32)); wme.update(); wme.validate()
water = bpy.data.objects.new("water", wme); sc.collection.objects.link(water)
wm = bpy.data.materials.new("water"); wm.use_nodes = True
wb = wm.node_tree.nodes["Principled BSDF"]
wb.inputs["Base Color"].default_value = (0.05, 0.42, 0.75, 1); wb.inputs["Roughness"].default_value = 0.15
water.data.materials.append(wm)
nframes = int(SECS * FPS)
sc.frame_start, sc.frame_end = 1, nframes
for f, lvl in [(1, full), (int(nframes * 0.25), full), (nframes, low)]:
    water.location.z = lvl; water.keyframe_insert("location", index=2, frame=f)

# ---- light + world ----
bpy.ops.object.light_add(type="SUN", rotation=(math.radians(62), 0, math.radians(-35)))
bpy.context.object.data.energy = 3.2; bpy.context.object.data.angle = math.radians(3)
world = bpy.data.worlds.new("w"); sc.world = world; world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.012, 0.02, 0.045, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.6
sc.view_settings.view_transform = "AgX"

# ---- camera: slow dolly up-valley from above the dam ----
bpy.ops.object.camera_add(); cam = bpy.context.object; sc.camera = cam
cam.data.lens = 32
target = bpy.data.objects.new("target", None); sc.collection.objects.link(target)
tc = cam.constraints.new("TRACK_TO"); tc.target = target
mid_x, mid_y = lonlat_to_xy(-99.30, 26.78)
zap_x, zap_y = lonlat_to_xy(-99.2714, 26.9073)
start = Vector((dam_x + 70, dam_y - 95, 85)); end = Vector((dam_x + 30, dam_y - 30, 62))
for f, pos, tg in [(1, start, (mid_x, mid_y - 40, 0)), (nframes, end, (zap_x, zap_y - 40, 0))]:
    cam.location = pos; cam.keyframe_insert("location", frame=f)
    target.location = tg; target.keyframe_insert("location", frame=f)
for ob in (cam, target):
    for fc in ob.animation_data.action.fcurves if hasattr(ob.animation_data.action, "fcurves") else []:
        for k in fc.keyframe_points: k.interpolation = "SINE"

# ---- render settings ----
r = sc.render; r.engine = "CYCLES"; r.resolution_x, r.resolution_y = RES; r.fps = FPS
sc.cycles.samples = 12; sc.cycles.use_denoising = True; sc.cycles.device = "CPU"
r.image_settings.file_format = "PNG"; r.filepath = os.path.join(fdir, "f")

labels = {"Falcon Dam": (-99.1683, 26.5575), "Zapata": (-99.2714, 26.9073)}
pts = {k: Vector((*lonlat_to_xy(*v), 0)) for k, v in labels.items()}
for k in pts: pts[k].z = height_at(pts[k].x, pts[k].y) + 1.5
out = {}
for f in range(1, nframes + 1):
    sc.frame_set(f)
    out[f] = {k: list(world_to_camera_view(sc, cam, p))[:3] for k, p in pts.items()}
json.dump(out, open(os.path.join(fdir, "labels.json"), "w"))

only = os.environ.get("ONLY_FRAME")
if only:
    sc.frame_set(int(only)); r.filepath = os.path.join(fdir, f"test_{only}.png")
    bpy.ops.render.render(write_still=True)
else:
    bpy.ops.render.render(animation=True)
print("terrain done")
