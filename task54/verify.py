"""Run from the repo root with pipeline dependencies and g++ on PATH.

Optional argv[1]: executable built from engine/horizon.cpp before this change.
"""
import gzip
import hashlib
import json
import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import numpy as np

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "pipeline"))
import build_field as field
import engine
import horizon as reference
from terrain import Terrain, to_latlon, to_map

OUT = Path(__file__).resolve().parent
DATA = ROOT / "web/public/data"
result = {}
names = ["field_north.json", "field_north.bin.gz", "heights_north.bin.gz", "slope_north.bin.gz"]
hashes = lambda: {name: hashlib.sha256((DATA / name).read_bytes()).hexdigest() for name in names}
before = hashes()
field.main("north")
assert hashes() == before
result["north_rebuild_byte_identical"] = True
result["north_sha256"] = hashes()

# Compare old and new Python builders in scratch, then report any pre-existing
# difference between a rebuild and the older committed production assets.
with tempfile.TemporaryDirectory() as scratch:
    scratch = Path(scratch)
    current, baseline_dir = scratch / "new", scratch / "baseline"
    with patch.object(field, "OUT", current):
        field.main()
    source = subprocess.check_output(["git", "show", "78f3732:pipeline/build_field.py"])
    baseline_path = scratch / "baseline_builder.py"
    baseline_path.write_bytes(source)
    spec = importlib.util.spec_from_file_location("baseline_builder", baseline_path)
    baseline = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(baseline)
    baseline.OUT = baseline_dir
    baseline.main()
    committed_differences = {}
    for name in ("field_pole.bin.gz", "heights_pole.bin.gz", "slope_pole.bin.gz"):
        a = gzip.decompress((current / name).read_bytes())
        assert a == gzip.decompress((baseline_dir / name).read_bytes()), name
        committed_differences[name] = int(np.count_nonzero(np.frombuffer(a, dtype=np.uint8) != np.frombuffer(gzip.decompress((DATA / name).read_bytes()), dtype=np.uint8)))
    assert json.loads((current / "field_pole.json").read_text()) == json.loads((baseline_dir / "field_pole.json").read_text()) == json.loads((DATA / "field_pole.json").read_text())
result["south_old_and_new_builder_arrays_and_metadata_identical"] = True
result["pre_existing_rebuild_vs_committed_byte_differences"] = committed_differences

n, x, y = field.grid_centers(field.EXTENT_M, field.CELL_M)
lat, lon = to_latlon(x.ravel(), y.ravel(), "north")
raw = engine.horizon(lat, lon, 180, hemisphere="north")
delta = np.frombuffer(gzip.decompress((DATA / "field_north.bin.gz").read_bytes()), dtype=np.uint8).reshape(180, n, n)
q = (np.cumsum(delta, axis=0) % 256).astype(np.uint8)
encoded = np.clip(np.round((raw + 8) / 0.1), 0, 255).astype(np.uint8)
np.testing.assert_array_equal(q.transpose(1, 2, 0).reshape(n * n, 180), encoded)
result["north_full_encoded_values_checked"] = int(raw.size)
result["raw_horizon_range_deg"] = [float(raw.min()), float(raw.max())]
result["clipped_above_17_5_deg"] = int((raw > 17.5).sum())

terrain = Terrain("north")
ids = np.linspace(0, n - 1, 7, dtype=int)
rr, cc = np.meshgrid(ids, ids, indexing="ij")
indices = (rr * n + cc).ravel()
with patch.object(reference, "ray_distances", return_value=reference.ray_distances(first_m=20, growth=0.02)):
    independent = reference.horizon(terrain, lat[indices], lon[indices], 180, chunk=4)
error = float(np.max(np.abs(raw[indices] - independent)))
assert error < 0.01, error
result["independent_python_points"] = 49
result["independent_python_max_error_deg"] = error

# North height data must agree at all mesh points; source north/south images
# are distinct, and their byte hashes are included for provenance.
_, mx, my = field.grid_centers(field.EXTENT_M, field.MESH_CELL_M)
heights = np.frombuffer(gzip.decompress((DATA / "heights_north.bin.gz").read_bytes()), dtype="<i2").reshape(1280, 1280)
expected = terrain.height_xy(mx, my)
height_error = float(np.max(np.abs(expected - heights)))
assert height_error <= 0.5
result["north_mesh_values_checked"] = int(expected.size)
result["north_mesh_max_rounding_error_m"] = height_error
result["north_raw_dem_sha256"] = {name: hashlib.sha256((ROOT / "data/raw" / name).read_bytes()).hexdigest() for name in ("ldem_85n_40m.img", "ldem_75n_240m.img")}

if len(sys.argv) > 1:
    # Native float comparison, including the old CLI with no hemisphere arg.
    south_lat, south_lon = to_latlon(x.ravel(), y.ravel())
    with tempfile.TemporaryDirectory() as scratch:
        pts = Path(scratch) / "points.f64"
        old = Path(scratch) / "old.f32"
        new = Path(scratch) / "new.f32"
        np.stack([south_lat, south_lon], axis=1).astype("<f8").tofile(pts)
        args = [str(engine.RAW), str(pts)]
        subprocess.run([sys.argv[1], *args, str(old), "180", "2", "250000"], check=True)
        subprocess.run([str(engine.EXE), *args, str(new), "180", "2", "250000"], check=True)
        assert old.read_bytes() == new.read_bytes()
    result["south_old_cli_raw_float_values_identical"] = n * n * 180

(OUT / "data-checks.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
