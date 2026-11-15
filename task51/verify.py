"""Run from the repository root with pipeline requirements installed and g++ on PATH."""
import gzip
import hashlib
import json
import sys
from pathlib import Path
from unittest.mock import patch

import numpy as np

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "pipeline"))
import build_site_field as builder
import engine
import horizon as reference
from terrain import Terrain, to_latlon

DATA = ROOT / "web/public/data"
NAMES = ["field_ridge_b.json", "field_ridge_b.bin.gz", "heights_ridge_b.bin.gz", "slope_ridge_b.bin.gz"]


def hashes():
    return {name: hashlib.sha256((DATA / name).read_bytes()).hexdigest() for name in NAMES}


def load(name):
    meta = json.loads((DATA / f"field_{name}.json").read_text())
    n, bins = meta["horizon"]["size"], meta["horizon"]["azimuthBins"]
    delta = np.frombuffer(gzip.decompress((DATA / meta["horizon"]["file"]).read_bytes()), dtype=np.uint8).reshape(bins, n, n)
    # The browser accumulates layers modulo 256 in-place.
    q = (np.cumsum(delta, axis=0) % 256).astype(np.uint8)
    return meta, q


before = hashes()
builder.main()
assert hashes() == before, "Rebuild changed output bytes"
meta, fine = load("ridge_b")
pole_meta, pole = load("pole")
cx, cy = meta["centerX"], meta["centerY"]
shared = []
for row in range(320):
    y = 40000 - (row + 0.5) * 250
    fr = (2500 - y + cy) / 20 - 0.5
    if fr < 0 or fr >= 250 or fr != round(fr):
        continue
    for col in range(320):
        x = (col + 0.5) * 250 - 40000
        fc = (x - cx + 2500) / 20 - 0.5
        if 0 <= fc < 250 and fc == round(fc):
            shared.append(np.abs(fine[:, int(fr), int(fc)].astype(int) - pole[:, row, col].astype(int)))
shared = np.array(shared) * 0.1
assert shared.shape == (100, 180)
assert shared.max() <= 0.3

n, x, y = builder.site_grid(20)
lat, lon = to_latlon(x.ravel(), y.ravel())
# Recompute all 11.25 million elevations with the unchanged production engine.
raw = engine.horizon(lat, lon, 180)
q = np.clip(np.round((raw + 8) / 0.1), 0, 255).astype(np.uint8)
np.testing.assert_array_equal(q.reshape(n, n, 180).transpose(2, 0, 1), fine)

# Independent vectorized Python implementation, using exactly the C++ ray
# distances (20 m initial step, 2% growth, 250 km limit). It does not use
# the C++ early-exit bound, byte encoding, or axis reshaping.
ids = np.linspace(0, n - 1, 7, dtype=int)
rr, cc = np.meshgrid(ids, ids, indexing="ij")
indices = (rr * n + cc).ravel()
distances = reference.ray_distances(first_m=20, growth=0.02)
with patch.object(reference, "ray_distances", return_value=distances):
    py = reference.horizon(Terrain(), lat[indices], lon[indices], 180, chunk=4)
independent_error = float(np.max(np.abs(raw[indices] - py)))
assert independent_error < 0.01, independent_error

# Validate all mesh heights against the measured DEM and both slope layers.
_, mx, my = builder.site_grid(5)
z = Terrain().height_xy(mx, my)
stored = np.frombuffer(gzip.decompress((DATA / meta["heights"]["file"]).read_bytes()), dtype="<i2").reshape(1000, 1000)
height_error = float(np.max(np.abs(stored - z)))
assert height_error <= 0.5
assert meta["heights"]["min"] == float(z.min())
assert meta["heights"]["max"] == float(z.max())
slope = np.frombuffer(gzip.decompress((DATA / meta["slope"]["file"]).read_bytes()), dtype=np.uint8).reshape(2, n, n)
assert slope[1].max() <= 100
assert slope[0].max() <= 255
np.testing.assert_array_equal(slope, builder.slope_layers(z))

unclipped = (raw >= -8) & (raw <= 17.5)
decoded = q.astype(float) * 0.1 - 8
quant_error = float(np.max(np.abs(decoded[unclipped] - raw[unclipped])))
assert quant_error <= 0.05001
result = {
    "rebuild_byte_identical": True,
    "sha256": hashes(),
    "shared_points": 100,
    "shared_direction_comparisons": 18000,
    "shared_max_error_deg": float(shared.max()),
    "shared_mean_error_deg": float(shared.mean()),
    "full_engine_comparisons": int(raw.size),
    "full_engine_encoded_bytes_equal": True,
    "independent_python_points": int(indices.size),
    "independent_python_max_error_deg": independent_error,
    "mesh_heights_checked": int(z.size),
    "max_height_rounding_error_m": height_error,
    "raw_horizon_range_deg": [float(raw.min()), float(raw.max())],
    "quantization_max_error_deg_unclipped": quant_error,
    "clipped_above_17_5_deg": int((raw > 17.5).sum()),
    "clipped_below_minus_8_deg": int((raw < -8).sum()),
    "compressed_bytes": {name: (DATA / name).stat().st_size for name in NAMES},
}
Path(__file__).with_name("data-checks.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
