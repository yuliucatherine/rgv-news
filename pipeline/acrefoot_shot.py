"""Blender: 'what is an acre-foot' - an American football field (with end zones, about 1.32 acres)
slowly filling with water to about 9 inches (one acre-foot spread over the field), camera orbiting.
Usage: python3 acrefoot_shot.py <frames_dir> [seconds] [fps]   (ONLY_FRAME=n renders one test frame)
"""
import sys, os, math
import bpy

fdir = sys.argv[1]; SECS = float(sys.argv[2]) if len(sys.argv) > 2 else 8; FPS = int(sys.argv[3]) if len(sys.argv) > 3 else 24
os.makedirs(fdir, exist_ok=True)
N = int(SECS * FPS)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.frame_start, sc.frame_end = 1, N
# units: 1 BU = 1 yard. Field 120 x 53.33 yd; depth exaggerated x8 so 9 in (0.25 yd) reads on screen
L, Wd, DEPTH, VEX = 120.0, 53.33, 0.25, 8.0


def mat(name, col, emit=0.0, rough=0.6, alpha=1.0, metal=0.0, transmission=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = tuple(col) + (1,)
    b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    if emit:
        (b.inputs.get("Emission Color") or b.inputs.get("Emission")).default_value = tuple(col) + (1,)
        b.inputs["Emission Strength"].default_value = emit
    if alpha < 1:
        b.inputs["Alpha"].default_value = alpha
    if transmission:
        (b.inputs.get("Transmission Weight") or b.inputs.get("Transmission")).default_value = transmission
    return m


# ground + field
bpy.ops.mesh.primitive_plane_add(size=1); g = bpy.context.object; g.scale = (400, 400, 1)
g.data.materials.append(mat("ground", (0.008, 0.012, 0.022), rough=0.95))
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.05)); f = bpy.context.object
f.scale = (L, Wd, 0.1); f.data.materials.append(mat("turf", (0.08, 0.32, 0.12), rough=0.85))
for ez in (-1, 1):   # end zones, darker
    bpy.ops.mesh.primitive_cube_add(size=1, location=(ez * 55, 0, 0.06)); e = bpy.context.object
    e.scale = (10, Wd, 0.1); e.data.materials.append(mat(f"ez{ez}", (0.06, 0.24, 0.10), rough=0.85))
white = mat("lines", (0.95, 0.95, 0.95), emit=0.4)
for yd in range(-50, 51, 5):   # yard lines
    bpy.ops.mesh.primitive_cube_add(size=1, location=(yd, 0, 0.12)); ln = bpy.context.object
    ln.scale = (0.25 if yd % 10 == 0 else 0.12, Wd, 0.02); ln.data.materials.append(white)
for s in (-1, 1):   # sidelines
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, s * Wd / 2, 0.12)); ln = bpy.context.object
    ln.scale = (L, 0.35, 0.02); ln.data.materials.append(white)
# glass walls so the water has a visible edge
glass = mat("glass", (0.8, 0.9, 1.0), rough=0.05, alpha=0.18)
for (x, y, sx, sy) in [(0, Wd / 2 + 0.3, L + 0.6, 0.15), (0, -Wd / 2 - 0.3, L + 0.6, 0.15),
                       (L / 2 + 0.3, 0, 0.15, Wd + 0.6), (-L / 2 - 0.3, 0, 0.15, Wd + 0.6)]:
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, DEPTH * VEX / 2 + 0.6)); w = bpy.context.object
    w.scale = (sx, sy, DEPTH * VEX + 1.0); w.data.materials.append(glass)
# water block rising
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.1)); wat = bpy.context.object
wat.data.transform(__import__("mathutils").Matrix.Translation((0, 0, 0.5)))
wat.scale = (L, Wd, 0.001); wat.keyframe_insert("scale", frame=max(1, int(N * 0.12)))
wat.scale = (L, Wd, DEPTH * VEX); wat.keyframe_insert("scale", frame=int(N * 0.78))
wat.data.materials.append(mat("water", (0.15, 0.6, 1.0), emit=0.06, rough=0.05, alpha=0.42))
for fc in (wat.animation_data.action.fcurves if hasattr(wat.animation_data.action, "fcurves") else []):
    for k in fc.keyframe_points: k.interpolation = "SINE"

bpy.ops.object.light_add(type="SUN"); sun = bpy.context.object; sun.data.energy = 2.2
sun.rotation_euler = (math.radians(50), math.radians(10), math.radians(30))
world = bpy.data.worlds.new("w"); sc.world = world; world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.012, 0.02, 0.045, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.0
sc.view_settings.view_transform = "Standard"

bpy.ops.object.camera_add(); cam = bpy.context.object; sc.camera = cam; cam.data.lens = 30
tgt = bpy.data.objects.new("t", None); sc.collection.objects.link(tgt); tgt.location = (0, 0, 0)
cam.constraints.new("TRACK_TO").target = tgt
for fr, ang, r, h in [(1, -125, 150, 70), (N, -70, 130, 52)]:   # slow orbit + push-in
    a = math.radians(ang); cam.location = (r * math.cos(a), r * math.sin(a), h); cam.keyframe_insert("location", frame=fr)

r = sc.render; r.engine = "CYCLES"; r.resolution_x, r.resolution_y = 960, 540; r.fps = FPS
sc.cycles.samples = 10; sc.cycles.use_denoising = True; sc.cycles.device = "CPU"
r.image_settings.file_format = "PNG"; r.filepath = os.path.join(fdir, "f")
only = os.environ.get("ONLY_FRAME")
if only:
    sc.frame_set(int(only)); r.filepath = os.path.join(fdir, f"test_{only}.png"); bpy.ops.render.render(write_still=True)
else:
    bpy.ops.render.render(animation=True)
print("acrefoot done")
