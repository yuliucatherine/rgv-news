"""Reusable Blender aerial flyover: real elevation draped with real aerial imagery, an optional
glowing route that draws itself, and named points exported for 2D labels. Options for distinct looks: "sun"
(elevation/azimuth/energy/color), "world_color", "imagery_tint", "camera.orbit" (one slow arc) and "dof".
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
if cfg.get("nodata_fill") == "mean" and nod.any() and (~nod).any():   # blank imagery (outside USGS coverage) as neutral ground
    im[nod] = im[~nod].mean(0)
im = im * cfg.get("imagery_gain", 1.08)
if cfg.get("imagery_tint"): im = im * np.array(cfg["imagery_tint"], np.float32)   # e.g. warm [1.08,0.96,0.82] for golden hour
Image.fromarray(np.clip(im, 0, 255).astype(np.uint8)).save(proc, quality=92)
mat = bpy.data.materials.new("terrain"); mat.use_nodes = True
nt = mat.node_tree; bsdf = nt.nodes["Principled BSDF"]
img = nt.nodes.new("ShaderNodeTexImage"); img.image = bpy.data.images.load(proc)
nt.links.new(img.outputs["Color"], bsdf.inputs["Base Color"])
bsdf.inputs["Roughness"].default_value = 1.0
em = bsdf.inputs.get("Emission Color") or bsdf.inputs.get("Emission")
nt.links.new(img.outputs["Color"], em); bsdf.inputs["Emission Strength"].default_value = cfg.get("imagery_glow", 0.35)
terrain.data.materials.append(mat)

# ---------- optional ground skirt: a huge flat plane in the terrain's average colour so the map edge never shows ----------
if cfg.get("skirt"):
    sk_ = cfg["skirt"] if isinstance(cfg["skirt"], dict) else {}
    pim = np.asarray(Image.open(proc).convert("RGB")).astype(np.float32)
    edge = np.concatenate([pim[:40].reshape(-1, 3), pim[-40:].reshape(-1, 3), pim[:, :40].reshape(-1, 3), pim[:, -40:].reshape(-1, 3)])
    srgb = np.array(sk_.get("color", (edge.mean(0) / 255).tolist()), np.float32)
    lin = np.where(srgb <= 0.04045, srgb / 12.92, ((srgb + 0.055) / 1.055) ** 2.4)
    bpy.ops.mesh.primitive_plane_add(size=sk_.get("size_bu", 9000), location=(0, 0, float(z.min()) - sk_.get("drop", 0.05)))
    skm = bpy.data.materials.new("skirt"); skm.use_nodes = True; sb = skm.node_tree.nodes["Principled BSDF"]
    sb.inputs["Base Color"].default_value = tuple(lin.tolist()) + (1,); sb.inputs["Roughness"].default_value = 1.0
    (sb.inputs.get("Emission Color") or sb.inputs.get("Emission")).default_value = tuple(lin.tolist()) + (1,)
    sb.inputs["Emission Strength"].default_value = cfg.get("imagery_glow", 0.35)
    bpy.context.object.data.materials.append(skm)

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
sun = cfg.get("sun", {})   # {"elevation": deg above horizon, "azimuth": deg, "energy": x, "color": [r,g,b], "angle": deg}
bpy.ops.object.light_add(type="SUN", rotation=(math.radians(90 - sun.get("elevation", 35)), 0, math.radians(sun.get("azimuth", -40))))
bpy.context.object.data.energy = sun.get("energy", 2.2)
bpy.context.object.data.color = tuple(sun.get("color", [1, 1, 1]))
bpy.context.object.data.angle = math.radians(sun.get("angle", 1.0))   # softer shadows when larger
world = bpy.data.worlds.new("w"); sc.world = world; world.use_nodes = True
bg = world.node_tree.nodes["Background"]; bg.inputs["Color"].default_value = tuple(cfg.get("world_color", [0.012, 0.02, 0.045])) + (1,)
bg.inputs["Strength"].default_value = cfg.get("world_strength", 0.8)
if cfg.get("sky"):   # physical sky gradient (Nishita) behind the horizon, e.g. dusk: {"sun_elevation": 4, "sun_rotation": 260, "strength": 0.25}
    sk = cfg["sky"]; tex = world.node_tree.nodes.new("ShaderNodeTexSky"); tex.sky_type = next(s for s in ("NISHITA", "MULTIPLE_SCATTERING", "SINGLE_SCATTERING") if s in [i.identifier for i in tex.bl_rna.properties["sky_type"].enum_items])
    tex.sun_elevation = math.radians(sk.get("sun_elevation", 5)); tex.sun_rotation = math.radians(sk.get("sun_rotation", 0))
    for k_, v_ in (("air_density", sk.get("air", 1.5)), ("dust_density", sk.get("dust", 2.0))):
        if hasattr(tex, k_): setattr(tex, k_, v_)
    world.node_tree.links.new(tex.outputs["Color"], bg.inputs["Color"]); bg.inputs["Strength"].default_value = sk.get("strength", 0.3)
sc.view_settings.view_transform = cfg.get("view_transform", "AgX")
mist = cfg.get("mist")
bpy.ops.object.camera_add(); cam = bpy.context.object; sc.camera = cam; cam.data.lens = cfg.get("lens", 30)
cam.data.clip_end = 5000
target = bpy.data.objects.new("target", None); sc.collection.objects.link(target)
tc = cam.constraints.new("TRACK_TO"); tc.target = target
orb = cfg["camera"].get("orbit")
if orb:   # one slow arc around a point: {"center": [lon,lat], "radius_m": m, "height": bu, "start_deg": a, "end_deg": b}
    cx, cy = ll(*orb["center"]); r_bu = orb["radius_m"] / SCALE; target.location = (cx, cy, zat(cx, cy))
    for f in range(1, nframes + 1):
        u = (f - 1) / max(1, nframes - 1); u = u * u * (3 - 2 * u) if orb.get("ease", True) else u
        a = math.radians(orb["start_deg"] + (orb["end_deg"] - orb["start_deg"]) * u)
        hgt = orb["height"] + (orb.get("end_height", orb["height"]) - orb["height"]) * u
        rr = r_bu * (1 + (orb.get("end_radius_scale", 1.0) - 1) * u)
        cam.location = (cx + rr * math.sin(a), cy - rr * math.cos(a), hgt); cam.keyframe_insert("location", frame=f)
    target.keyframe_insert("location", frame=1)
else:
    for f_rel, key in [(0, "start"), (1, "end")]:
        c = cfg["camera"][key]
        x, y = ll(*c["over"]); tx, ty = ll(*c["look_at"])
        cam.location = (x, y, c["height"]); target.location = (tx, ty, zat(tx, ty))
        f = 1 if f_rel == 0 else nframes
        cam.keyframe_insert("location", frame=f); target.keyframe_insert("location", frame=f)
if cfg.get("dof"):   # miniature / tabletop look: focus on the target, shallow depth of field
    cam.data.dof.use_dof = True; cam.data.dof.focus_object = target; cam.data.dof.aperture_fstop = cfg["dof"].get("fstop", 2.0)

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
    r.use_overwrite = False   # resume: skip frames already on disk
    bpy.ops.render.render(animation=True)
print("geo shot done")
