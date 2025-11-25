import bpy
import json
import mathutils
import sys

ATOM_RADIUS = 0.3
BOND_RADIUS = 0.1
BOND_SHRINK = 0.05

json_path = sys.argv[-2]
usdz_path = sys.argv[-1]

# Reset scene
bpy.ops.wm.read_factory_settings(use_empty=True)

with open(json_path, "r") as f:
    data = json.load(f)

# Atom colors
colors = {
    "H": (1, 1, 1, 1),
    "C": (0.2, 0.2, 0.2, 1),
    "N": (0.1, 0.1, 1.0, 1),
    "O": (1.0, 0.1, 0.1, 1),
    "S": (1.0, 0.9, 0.1, 1),
    "P": (1.0, 0.5, 0.0, 1),
}

# Add atoms
for atom in data["atoms"]:
    bpy.ops.mesh.primitive_uv_sphere_add(radius=ATOM_RADIUS, location=atom["position"])
    obj = bpy.context.object
    col = colors.get(atom["symbol"], (0.8, 0.8, 0.8, 1))
    mat = bpy.data.materials.new(name=atom["symbol"])
    mat.diffuse_color = col
    obj.data.materials.append(mat)

# Add bonds
for i, j in data["bonds"]:
    a = mathutils.Vector(data["atoms"][i]["position"])
    b = mathutils.Vector(data["atoms"][j]["position"])
    vec = b - a
    length = vec.length * (1 - BOND_SHRINK)
    mid = (a + b) / 2

    bpy.ops.mesh.primitive_cylinder_add(radius=BOND_RADIUS, depth=length, location=mid)
    obj = bpy.context.object
    up = mathutils.Vector((0, 0, 1))
    quat = up.rotation_difference(vec.normalized())
    obj.rotation_mode = 'QUATERNION'
    obj.rotation_quaternion = quat
    mat = bpy.data.materials.new(name="Bond")
    mat.diffuse_color = (0.7, 0.7, 0.7, 1)
    obj.data.materials.append(mat)

# Export
bpy.ops.wm.usd_export(filepath=usdz_path)
bpy.ops.wm.quit_blender()
print("✅ Blender export complete:", usdz_path)

