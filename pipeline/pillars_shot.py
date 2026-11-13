"""Blender 3D 'investment pillars' map: an extruded state with glowing columns that grow to heights
proportional to dollar amounts. Driven by a JSON config; writes PNG frames + labels.json.
Usage: python3 pillars_shot.py <config.json> <frames_dir>     (ONLY_FRAME=n for a test frame)
Boundary: U.S. Census Bureau cartographic boundary (public domain).
"""
import sys, os, json, math
import numpy as np, geopandas as gpd
import bpy, bmesh
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

cfg = json.load(open(sys.argv[1])); fdir = sys.argv[2]; os.makedirs(fdir, exist_ok=True)
FPS, SECS = cfg.get("fps", 24), cfg.get("seconds", 8)
KM = cfg.get("km_per_unit", 5.0)
st = gpd.read_file(cfg["states_zip"]).to_crs(3857)
state = st[st.STUSPS == cfg.get("state", "TX")].geometry.iloc[0].simplify(cfg.get("simplify_m", 1500))
cx, cy = state.centroid.x, state.centroid.y


def xy(lon, lat):
    from pyproj import Transformer
    x, y = Transformer.from_crs(4326, 3857, always_xy=True).transform(lon, lat)
    return (x - cx) / 1000 / KM, (y - cy) / 1000 / KM


bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene


def mat(name, base, emit=None, strength=0.0, rough=0.6):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = base + (1,); b.inputs["Roughness"].default_value = rough
    if emit:
        (b.inputs.get("Emission Color") or b.inputs.get("Emission")).default_value = emit + (1,)
        b.inputs["Emission Strength"].default_value = strength
    return m


# ---- extruded state slab ----
THICK = cfg.get("slab_thickness", 3.0)
polys = list(getattr(state, "geoms", [state]))
slab_mat = mat("slab", (0.035, 0.06, 0.11), rough=0.7)
edge_mat = mat("edge", (0.1, 0.15, 0.22), emit=(0.35, 0.55, 0.8), strength=1.2)
for k, p in enumerate(polys):
    coords = [((x - cx) / 1000 / KM, (y - cy) / 1000 / KM) for x, y in list(p.exterior.coords)[:-1]]
    if len(coords) < 3: continue
    bm = bmesh.new()
    vs = [bm.verts.new((x, y, 0)) for x, y in coords]
    face = bm.faces.new(vs)
    ext = bmesh.ops.extrude_face_region(bm, geom=[face])
    bmesh.ops.translate(bm, verts=[v for v in ext["geom"] if isinstance(v, bmesh.types.BMVert)], vec=(0, 0, THICK))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(f"slab{k}"); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(f"slab{k}", me); sc.collection.objects.link(ob); ob.data.materials.append(slab_mat)
    # glowing outline along the top edge
    cu = bpy.data.curves.new(f"edge{k}", "CURVE"); cu.dimensions = "3D"
    sp = cu.splines.new("POLY"); sp.points.add(len(coords)); sp.use_cyclic_u = True
    for i, (x, y) in enumerate(coords + [coords[0]]): sp.points[i].co = (x, y, THICK + 0.05, 1)
    cu.bevel_depth = cfg.get("edge_width", 0.35)
    eo = bpy.data.objects.new(f"edge{k}", cu); sc.collection.objects.link(eo); eo.data.materials.append(edge_mat)

# ---- pillars ----
nframes = int(SECS * FPS); sc.frame_start, sc.frame_end = 1, nframes
maxv = max(p["value"] for p in cfg["pillars"])
labels = {}
for i, p in enumerate(cfg["pillars"]):
    x, y = xy(p["lon"], p["lat"])
    hgt = cfg.get("max_height", 70.0) * p["value"] / maxv
    bpy.ops.mesh.primitive_cylinder_add(radius=cfg.get("radius", 3.2), depth=1, vertices=48, location=(x, y, THICK))
    ob = bpy.context.object
    # put the origin at the base so scaling grows upward
    ob.data.transform(__import__("mathutils").Matrix.Translation((0, 0, 0.5)))
    col = tuple(p.get("color", [0.98, 0.45, 0.09]))
    ob.data.materials.append(mat(f"p{i}", col, emit=col, strength=p.get("glow", 2.5), rough=0.3))
    f0 = int(nframes * p.get("grow", [0.2, 0.6])[0]); f1 = int(nframes * p.get("grow", [0.2, 0.6])[1])
    ob.scale = (1, 1, 0.001); ob.keyframe_insert("scale", frame=max(1, f0))
    ob.scale = (1, 1, hgt); ob.keyframe_insert("scale", frame=f1)
    # base ring marker
    bpy.ops.mesh.primitive_cylinder_add(radius=cfg.get("radius", 3.2) * 1.9, depth=0.15, vertices=48, location=(x, y, THICK + 0.08))
    bpy.context.object.data.materials.append(mat(f"r{i}", col, emit=col, strength=0.8, rough=0.5))
    labels[p["label"]] = (x, y, THICK + hgt + 2.0)

# ---- light/world/camera ----
bpy.ops.object.light_add(type="SUN", rotation=(math.radians(50), 0, math.radians(30))); bpy.context.object.data.energy = 2.5
world = bpy.data.worlds.new("w"); sc.world = world; world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.012, 0.02, 0.045, 1)
bpy.ops.mesh.primitive_plane_add(size=4000, location=(0, 0, -0.05))
bpy.context.object.data.materials.append(mat("floor", (0.015, 0.025, 0.05), rough=0.9))
sc.view_settings.view_transform = "Standard"
bpy.ops.object.camera_add(); cam = bpy.context.object; sc.camera = cam; cam.data.lens = cfg.get("lens", 35)
cam.data.clip_end = 10000
tgt = bpy.data.objects.new("t", None); sc.collection.objects.link(tgt)
cam.constraints.new("TRACK_TO").target = tgt
for f, key in [(1, "start"), (nframes, "end")]:
    c = cfg["camera"][key]
    tx, ty = xy(*c["look_at"])
    a = math.radians(c["azimuth"]); r_ = c["distance"]
    cam.location = (tx + r_ * math.sin(a), ty - r_ * math.cos(a), c["height"]); tgt.location = (tx, ty, c.get("look_z", 10))
    cam.keyframe_insert("location", frame=f); tgt.keyframe_insert("location", frame=f)

r = sc.render; r.engine = "CYCLES"; r.resolution_x, r.resolution_y = tuple(cfg.get("resolution", [1280, 720])); r.fps = FPS
sc.cycles.samples = cfg.get("samples", 16); sc.cycles.use_denoising = True; sc.cycles.device = "CPU"
r.image_settings.file_format = "PNG"; r.filepath = os.path.join(fdir, "f")

out = {}
pill_objs = [o for o in sc.objects if o.name.startswith("Cylinder") and o.dimensions.z > 0]
for f in range(1, nframes + 1):
    sc.frame_set(f); fr = {}
    for (lab, (x, y, ztop)), p in zip(labels.items(), cfg["pillars"]):
        # follow the growing top
        f0 = int(nframes * p.get("grow", [0.2, 0.6])[0]); f1 = int(nframes * p.get("grow", [0.2, 0.6])[1])
        g = min(1, max(0, (f - f0) / max(1, f1 - f0))); g = g * g * (3 - 2 * g)
        z = THICK + (ztop - THICK - 2.0) * g + 2.0
        fr[lab] = list(world_to_camera_view(sc, cam, Vector((x, y, z))))[:3] + [g]
    out[f] = fr
json.dump(out, open(os.path.join(fdir, "labels.json"), "w"))
only = os.environ.get("ONLY_FRAME")
if only:
    sc.frame_set(int(only)); r.filepath = os.path.join(fdir, f"test_{only}.png"); bpy.ops.render.render(write_still=True)
else:
    bpy.ops.render.render(animation=True)
print("pillars done")
