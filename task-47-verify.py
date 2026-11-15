import hashlib
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

repo, baseline, output = map(Path, sys.argv[1:4])
data = repo / "web" / "public" / "data"
meta = json.loads((data / "ephem.json").read_text())
old_meta = json.loads((baseline / "ephem.json").read_text())
start = datetime.fromisoformat(meta["start"].replace("Z", "+00:00"))
end = datetime(2037, 1, 1, tzinfo=timezone.utc)
expected_count = int((end - start).total_seconds() / 3600)
assert meta["count"] == expected_count == 96432
assert meta["stepHours"] == 1
assert meta["frame"] == old_meta["frame"] == "MOON_ME_DE421"
assert meta["dsn"] == old_meta["dsn"]
vectors = np.fromfile(data / "ephem.bin", dtype="<f4").reshape(-1, 6)
dsn = np.fromfile(data / "dsn.bin", dtype=np.int8).reshape(-1, 3)
assert vectors.shape == (expected_count, 6)
assert dsn.shape == (expected_count, 3)
assert np.isfinite(vectors).all()
assert np.all((dsn >= -90) & (dsn <= 90))
sun_dist = np.linalg.norm(vectors[:, :3].astype(np.float64), axis=1)
earth_dist = np.linalg.norm(vectors[:, 3:].astype(np.float64), axis=1)
assert np.all((sun_dist > 1.4e8) & (sun_dist < 1.6e8))
assert np.all((earth_dist > 350000) & (earth_dist < 410000))
old_vectors = np.fromfile(baseline / "ephem.bin", dtype="<f4").reshape(-1, 6)
old_dsn = np.fromfile(baseline / "dsn.bin", dtype=np.int8).reshape(-1, 3)
vector_prefix = vectors[:len(old_vectors)]
dsn_delta = dsn[:len(old_dsn)].astype(int) - old_dsn.astype(int)
samples = []
for date in [datetime(2036, 1, 1, tzinfo=timezone.utc), datetime(2036, 6, 1, tzinfo=timezone.utc), datetime(2036, 12, 1, tzinfo=timezone.utc), end - timedelta(hours=1)]:
    hour = int((date - start).total_seconds() / 3600)
    samples.append({"date": date.isoformat(), "hour": hour, "sunKm": vectors[hour, :3].tolist(), "earthKm": vectors[hour, 3:].tolist(), "dsnDeg": dsn[hour].tolist()})
report = {
    "start": meta["start"], "lastSample": (end - timedelta(hours=1)).isoformat(),
    "count": expected_count, "textureRows4096": int(np.ceil(expected_count / 4096)),
    "sunDistanceRangeKm": [float(sun_dist.min()), float(sun_dist.max())],
    "earthDistanceRangeKm": [float(earth_dist.min()), float(earth_dist.max())],
    "originalVectorPrefixIdentical": bool(np.array_equal(old_vectors, vector_prefix)),
    "originalVectorMaxDifferenceKm": float(np.max(np.abs(old_vectors.astype(float) - vector_prefix))),
    "originalDsnPrefixIdentical": bool(not np.any(dsn_delta)),
    "originalDsnChangedValues": int(np.count_nonzero(dsn_delta)),
    "originalDsnMaxDifferenceDeg": int(np.abs(dsn_delta).max()),
    "files": {name: {"bytes": (data / name).stat().st_size, "sha256": hashlib.sha256((data / name).read_bytes()).hexdigest()} for name in ["ephem.bin", "dsn.bin", "ephem.json"]},
    "samples": samples,
}
output.mkdir(parents=True, exist_ok=True)
(output / "data-integrity.json").write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
