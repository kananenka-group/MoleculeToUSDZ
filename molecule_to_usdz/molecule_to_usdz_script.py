#!/usr/bin/env python3
import json
import os
import sys
import tempfile
import subprocess
from pathlib import Path
from time import time
from ase.data import covalent_radii, atomic_numbers

# -------- CONFIGURATION -------- #
BLENDER_EXEC = "/Applications/Blender.app/Contents/MacOS/Blender"  # Update if needed
ATOM_RADIUS = 0.3
BOND_RADIUS = 0.1
BOND_SHRINK = 0.05  # fraction of bond length trimmed to avoid overlap
# -------------------------------- #

def run(cmd, check=True):
    """Run a system command and print it."""
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=check)

def notify_mac(title, message):
    """Show a macOS notification using AppleScript."""
    subprocess.run([
        "osascript", "-e", f'display notification "{message}" with title "{title}"'
    ])

def convert_to_json(input_path, json_path):
    """Convert PDB or XYZ to JSON (atoms + bonds) using ASE."""
    ext = Path(input_path).suffix.lower()
    if ext not in [".pdb", ".xyz"]:
        raise ValueError("Unsupported file type. Use .pdb or .xyz")

    script = f"""
from ase.io import read
from ase.data import covalent_radii, atomic_numbers
import json
import numpy as np

atoms = read("{input_path}")
data = {{"atoms": [], "bonds": []}}

for atom in atoms:
    symbol = getattr(atom, "symbol", "").strip()
    if not symbol or symbol == "?":
        # fallback for cases like C1, O2, etc.
        name = getattr(atom, "tag", "") or str(getattr(atom, "index", ""))
        symbol = name[0].capitalize() if name else "C"

    Z = atomic_numbers.get(symbol, 6)
    cov_rad = covalent_radii[Z]

    data["atoms"].append({{
        "symbol": symbol,
        "position": atom.position.tolist(),
        "radius": float(cov_rad)
    }})

for i, a1 in enumerate(data["atoms"]):
    for j, a2 in enumerate(data["atoms"]):
        if j <= i:
            continue
        d = np.linalg.norm(np.array(a1["position"]) - np.array(a2["position"]))
        if d < 1.2 * (a1["radius"] + a2["radius"]):
            data["bonds"].append([i, j])

with open("{json_path}", "w") as f:
    json.dump(data, f)
"""
    python_exe = sys.executable
    run([python_exe, "-c", script])

def run_blender_export(json_path, usdz_path):
    """Launch Blender to import atoms and bonds, then export as USDZ."""
    blender_script = f"""
import bpy, json, mathutils

bpy.ops.wm.read_factory_settings(use_empty=True)

with open(r"{json_path}", "r") as f:
    data = json.load(f)

colors = {{
    "H": (1.0, 1.0, 1.0, 1),
    "C": (0.2, 0.2, 0.2, 1),
    "N": (0.1, 0.1, 1.0, 1),
    "O": (1.0, 0.1, 0.1, 1),
    "S": (1.0, 0.9, 0.1, 1),
    "P": (1.0, 0.5, 0.0, 1),
}}

# Atoms
for atom in data["atoms"]:
    bpy.ops.mesh.primitive_uv_sphere_add(radius={ATOM_RADIUS}, location=atom["position"])
    obj = bpy.context.object
    col = colors.get(atom["symbol"], (0.8, 0.8, 0.8, 1))
    mat = bpy.data.materials.new(name=atom["symbol"])
    mat.diffuse_color = col
    obj.data.materials.append(mat)

# Bonds
for i, j in data["bonds"]:
    a = mathutils.Vector(data["atoms"][i]["position"])
    b = mathutils.Vector(data["atoms"][j]["position"])
    vec = b - a
    length = vec.length * (1 - {BOND_SHRINK})
    mid = (a + b) / 2.0

    bpy.ops.mesh.primitive_cylinder_add(
        radius={BOND_RADIUS},
        depth=length,
        location=mid
    )

    obj = bpy.context.object
    up = mathutils.Vector((0, 0, 1))
    quat = up.rotation_difference(vec.normalized())
    obj.rotation_mode = 'QUATERNION'
    obj.rotation_quaternion = quat

    mat = bpy.data.materials.new(name="Bond")
    mat.diffuse_color = (0.7, 0.7, 0.7, 1)
    obj.data.materials.append(mat)

bpy.ops.wm.usd_export(filepath=r"{usdz_path}")
bpy.ops.wm.quit_blender()
"""
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as tmp:
        tmp.write(blender_script)
        tmp_path = tmp.name

    run([BLENDER_EXEC, "--background", "--python", tmp_path])
    os.remove(tmp_path)

def convert_molecule_to_usdz(input_path):
    """Full pipeline: PDB/XYZ → JSON → Blender → USDZ + notification."""
    start = time()
    input_path = Path(input_path)
    usdz_path = input_path.with_suffix(".usdz")

    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = Path(tmpdir) / "molecule.json"
        convert_to_json(input_path, json_path)
        run_blender_export(json_path, usdz_path)

    elapsed = time() - start
    msg = f"{input_path.stem}.usdz ready in {elapsed:.2f} seconds"
    print(f"✅ Conversion complete: {usdz_path}")
    print(f"⏱️ Elapsed time: {elapsed:.2f} seconds")

    notify_mac("Molecule to USDZ", msg)
    return elapsed

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_molecule_to_usdz.py input.pdb|input.xyz")
        sys.exit(1)

    convert_molecule_to_usdz(sys.argv[1])
