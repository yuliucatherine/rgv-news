"""Reusable Blender aerial flyover: real elevation draped with real aerial imagery, an optional
glowing route that draws itself, and named points exported for 2D labels.
Driven by a JSON config (see shots/*.json). Writes PNG frames + labels.json.
Usage: python3 geo_shot.py <config.json> <frames_dir>      (env ONLY_FRAME=n renders one test frame)
"""
import sys, os, json, math
import numpy as np
import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
from PIL import Image

cfg = json.load(open(sys.argv[1])); fdir = sys.argv[2]; os.makedirs(fdir, exist_ok=True)
tdir = cfg["terrain_dir"]; meta = json.load(open(f"{tdir}/meta.json"))
SCALE, VEX = cfg.get("metres_per_unit", 50.0), cfg.get("vertical_exaggeration", 8.0)
FPS, SECS = cfg.get("fps", 24), cfg.get("seconds", 7)
RES = tuple(cfg.get("resolution", [1280, 720]))
DS = cfg.get("downsample", 4)

# ---------- terrain heights ----------
h = np.load(f"{tdir}/height.npy")[::DS, ::DS].astype(np.float64)
h = np.clip(h, cfg.get("min_elev", -1.0), None)          # ocean/no-data -> flat
ny, nx = h.shape
W_bu, H_bu = meta["width_m"] / SCALE, meta["height_m"] / SCALE
z = (h - h.min()) / SCALE * VEX


def merc(la): return math.log(math.tan(math.pi / 4 + math.radians(la) / 2))


def ll(lon, lat):
    fx = (lon - meta["lon0"]) / (meta["lon1"] - meta["lon0"])
    fy = (merc(lat) - merc(meta["lat0"])) / (merc(meta["lat1"]) - merc(meta["lat0"]))
    return (fx - 0.5) * W_bu, (fy - 0.5) * H_bu


def zat(x, y):
    i = int(round((0.5 - y / H_bu) * (ny - 1))); j = int(round((x / W_bu + 0.5) * (nx - 1)))
    return float(z[min(max(i, 0), ny - 1), min(max(j, 0), nx - 1)])


bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene

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
uv = me.uv_layers.new(name="uv")
U = (X - X.min()) / (X.max() - X.min()); V = (Y - Y.min()) / (Y.max() - Y.min())
uvv = np.stack([U, V], -1).reshape(-1, 2)[quads.ravel()]
uv.data.foreach_set("uv", uvv.astype(np.float32).ravel())
terrain = bpy.data.objects.new("terrain", me); sc.collection.objects.link(terrain)

# ---------- imagery: shade no-data (outside U.S. coverage) dark, like the 2D maps ----------
tex_src = cfg.get("texture", f"{tdir}/texture.jpg")
proc = os.path.join(fdir, "_texture.jpg")
im = np.asarray(Image.open(tex_src).convert("RGB")).astype(np.float32)
nod = (im.min(-1) > 245)
im[nod] = (14, 22, 40)
im = im * cfg.get("imagery_gain", 1.08)
Image.fromarray(np.clip(im, 0, 255).astype(np.uint8)).save(proc, quality=92)
mat = bpy.data.materials.new("terrain"); mat.use_nodes = True
nt = mat.node_tree; bsdf = nt.nodes["Principled BSDF"]
img = nt.nodes.new("ShaderNodeTexImage"); img.image = bpy.data.images.load(proc)
nt.links.new(img.outputs["Color"], bsdf.inputs["Base Color"])
bsdf.inputs["Roughness"].default_value = 1.0
em = bsdf.inputs.get("Emission Color") or bsdf.inputs.get("Emission")
nt.links.new(img.outputs["Color"], em); bsdf.inputs["Emission Strength"].default_value = cfg.get("imagery_glow", 0.35)
terrain.data.materials.append(mat)

nframes = int(SECS * FPS); sc.frame_start, sc.frame_end = 1, nframes

# ---------- glowing route that draws itself ----------
for k, route in enumerate(cfg.get("routes", [])):
    pts = route["points"]  # [[lon,lat],...]
    cu = bpy.data.curves.new(f"route{k}", "CURVE"); cu.dimensions = "3D"
    sp = cu.splines.new("POLY"); sp.points.add(len(pts) - 1)
    for i, (lon, lat) in enumerate(pts):
        x, y = ll(lon, lat); sp.points[i].co = (x, y, zat(x, y) + route.get("lift", 0.6), 1)
    cu.bevel_depth = route.get("width", 0.35); cu.bevel_resolution = 2
    ob = bpy.data.objects.new(f"route{k}", cu); sc.collection.objects.link(ob)
    m = bpy.data.materials.new(f"route{k}"); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    col = tuple(route.get("color", [1.0, 0.45, 0.09])) + (1,)
    b.inputs["Base Color"].default_value = col
    (b.inputs.get("Emission Color") or b.inputs.get("Emission")).default_value = col
    b.inputs["Emission Strength"].default_value = route.get("glow", 8)
    ob.data.materials.append(m)
    f0, f1 = [int(v * nframes) for v in route.get("draw", [0.15, 0.8])]
    cu.bevel_factor_end = 0.0; cu.keyframe_insert("bevel_factor_end", frame=max(1, f0))
    cu.bevel_factor_end = 1.0; cu.keyframe_insert("bevel_factor_end", frame=max(2, f1))

# ---------- light, world, camera ----------
bpy.ops.object.light_add(type="SUN", rotation=(math.radians(55), 0, math.radians(-40)))
bpy.context.object.data.energy = 2.2
world = bpy.data.worlds.new("w"); sc.world = world; world.use_nodes = True
bg = world.node_tree.nodes["Background"]; bg.inputs["Color"].default_value = (0.012, 0.02, 0.045, 1)
bg.inputs["Strength"].default_value = 0.8
sc.view_settings.view_transform = cfg.get("view_transform", "AgX")
mist = cfg.get("mist")
bpy.ops.object.camera_add(); cam = bpy.context.object; sc.camera = cam; cam.data.lens = cfg.get("lens", 30)
cam.data.clip_end = 5000
target = bpy.data.objects.new("target", None); sc.collection.objects.link(target)
tc = cam.constraints.new("TRACK_TO"); tc.target = target
for f_rel, key in [(0, "start"), (1, "end")]:
    c = cfg["camera"][key]
    x, y = ll(*c["over"]); tx, ty = ll(*c["look_at"])
    cam.location = (x, y, c["height"]); target.location = (tx, ty, zat(tx, ty))
    f = 1 if f_rel == 0 else nframes
    cam.keyframe_insert("location", frame=f); target.keyframe_insert("location", frame=f)

r = sc.render; r.engine = "CYCLES"; r.resolution_x, r.resolution_y = RES; r.fps = FPS
sc.cycles.samples = cfg.get("samples", 12); sc.cycles.use_denoising = True; sc.cycles.device = "CPU"
r.image_settings.file_format = "PNG"; r.filepath = os.path.join(fdir, "f")

out = {}
pts = {}
for p in cfg.get("labels", []):
    x, y = ll(p["lon"], p["lat"]); pts[p["name"]] = Vector((x, y, zat(x, y) + 1.0))
for f in range(1, nframes + 1):
    sc.frame_set(f)
    out[f] = {k: list(world_to_camera_view(sc, cam, v))[:3] for k, v in pts.items()}
json.dump(out, open(os.path.join(fdir, "labels.json"), "w"))
only = os.environ.get("ONLY_FRAME")
if only:
    sc.frame_set(int(only)); r.filepath = os.path.join(fdir, f"test_{only}.png"); bpy.ops.render.render(write_still=True)
else:
    bpy.ops.render.render(animation=True)
print("geo shot done")
