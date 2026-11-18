"""Blender 3D data columns: glowing columns that grow (optionally stacked segments) on a dark
reflective floor with a slow camera move. Driven by JSON; writes PNG frames + labels.json
(screen position of each column top, with growth factor, for overlay.py counting labels).
Usage: python3 bars_shot.py <config.json> <frames_dir>     (ONLY_FRAME=n renders one test frame)

config: {"seconds":8,"fps":24,"max_height":10,"spacing":4.5,"radius":1.1,
         "bars":[{"label":"Brownsville","segments":[{"value":122400,"color":[0.98,0.45,0.09]}],
                  "grow":[0.15,0.55]}, ...],
         "camera":{"start":{"pos":[x,y,z],"look":[x,y,z]},"end":{...}}}
"""
import sys, os, json, math
import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector, Matrix

cfg = json.load(open(sys.argv[1])); fdir = sys.argv[2]; os.makedirs(fdir, exist_ok=True)
FPS, SECS = cfg.get("fps", 24), cfg.get("seconds", 8)
nframes = int(FPS * SECS)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.frame_start, sc.frame_end = 1, nframes


def mat(name, base, emit=None, strength=0.0, rough=0.5, metal=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = tuple(base) + (1,); b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        (b.inputs.get("Emission Color") or b.inputs.get("Emission")).default_value = tuple(emit) + (1,)
        b.inputs["Emission Strength"].default_value = strength
    return m


# floor + faint grid lines
bpy.ops.mesh.primitive_plane_add(size=400)
bpy.context.object.data.materials.append(mat("floor", (0.02, 0.035, 0.07), rough=0.25, metal=0.3))
grid = mat("grid", (0.1, 0.15, 0.25), emit=(0.25, 0.38, 0.6), strength=0.35)
for i in range(-20, 21):
    for rot in (0, 90):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.01))
        o = bpy.context.object; o.scale = (200, 0.02, 0.005) if rot == 0 else (0.02, 200, 0.005)
        o.location = (0, i * 5, 0.01) if rot == 0 else (i * 5, 0, 0.01)
        o.data.materials.append(grid)

bars = cfg["bars"]; n = len(bars)
sp = cfg.get("spacing", 4.5); R = cfg.get("radius", 1.1); MH = cfg.get("max_height", 10.0)
maxv = max(sum(s["value"] for s in b["segments"]) for b in bars)
labels = {}
for i, b in enumerate(bars):
    x = (i - (n - 1) / 2) * sp
    base = 0.0
    g0, g1 = b.get("grow", [0.15, 0.55])
    segs = b["segments"]
    for k, s in enumerate(segs):
        h = MH * s["value"] / maxv
        bpy.ops.mesh.primitive_cylinder_add(radius=R, depth=1, vertices=64, location=(x, 0, base))
        o = bpy.context.object
        o.data.transform(Matrix.Translation((0, 0, 0.5)))
        col = s.get("color", [0.98, 0.45, 0.09])
        o.data.materials.append(mat(f"b{i}{k}", col, emit=col, strength=s.get("glow", 0.55), rough=0.35))
        # each stacked segment grows in its own slice of the bar's grow window
        a0 = g0 + (g1 - g0) * k / len(segs); a1 = g0 + (g1 - g0) * (k + 1) / len(segs)
        f0, f1 = max(1, int(nframes * a0)), max(2, int(nframes * a1))
        o.scale = (1, 1, 0.001); o.keyframe_insert("scale", frame=f0)
        o.scale = (1, 1, h); o.keyframe_insert("scale", frame=f1)
        base += h
    # glowing base ring
    bpy.ops.mesh.primitive_cylinder_add(radius=R * 1.6, depth=0.06, vertices=64, location=(x, 0, 0.03))
    c0 = segs[0].get("color", [0.98, 0.45, 0.09])
    bpy.context.object.data.materials.append(mat(f"r{i}", c0, emit=c0, strength=0.6))
    labels[b["label"]] = (x, base, g0, g1)

bpy.ops.object.light_add(type="AREA", location=(0, -12, 18)); L = bpy.context.object
L.data.energy = 2500; L.data.size = 20; L.rotation_euler = (math.radians(35), 0, 0)
world = bpy.data.worlds.new("w"); sc.world = world; world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.01, 0.018, 0.04, 1)
sc.view_settings.view_transform = "Standard"

bpy.ops.object.camera_add(); cam = bpy.context.object; sc.camera = cam; cam.data.lens = cfg.get("lens", 35)
tgt = bpy.data.objects.new("t", None); sc.collection.objects.link(tgt)
cam.constraints.new("TRACK_TO").target = tgt
for f, key in [(1, "start"), (nframes, "end")]:
    c = cfg["camera"][key]; cam.location = c["pos"]; tgt.location = c["look"]
    cam.keyframe_insert("location", frame=f); tgt.keyframe_insert("location", frame=f)

r = sc.render; r.engine = "CYCLES"; r.resolution_x, r.resolution_y = tuple(cfg.get("resolution", [1280, 720])); r.fps = FPS
sc.cycles.samples = cfg.get("samples", 24); sc.cycles.use_denoising = True; sc.cycles.device = "CPU"
r.image_settings.file_format = "PNG"; r.filepath = os.path.join(fdir, "f")

out = {}
for f in range(1, nframes + 1):
    sc.frame_set(f); fr = {}
    for lab, (x, top, g0, g1) in labels.items():
        g = min(1, max(0, (f / nframes - g0) / max(1e-6, g1 - g0))); g = g * g * (3 - 2 * g)
        fr[lab] = list(world_to_camera_view(sc, cam, Vector((x, 0, top * g + 0.8))))[:3] + [g]
    out[f] = fr
json.dump(out, open(os.path.join(fdir, "labels.json"), "w"))
only = os.environ.get("ONLY_FRAME")
if only:
    sc.frame_set(int(only)); r.filepath = os.path.join(fdir, f"test_{only}.png"); bpy.ops.render.render(write_still=True)
else:
    r.use_overwrite = False   # resume: skip frames already on disk
    bpy.ops.render.render(animation=True)
print("bars done")
