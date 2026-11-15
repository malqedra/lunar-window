import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

repo, output = map(Path, sys.argv[1:3])
sys.path.insert(0, str(repo / "pipeline"))
from validate_horizons import query, angle_diff
from horizon import altaz
from sites import SITES

vectors = np.fromfile(repo / "web/public/data/ephem.bin", dtype="<f4").reshape(-1, 6)
start = datetime(2026, 1, 1, tzinfo=timezone.utc)
report = []
for site in [s for s in SITES if s["id"] in ("connecting-ridge-b", "malapert-m1", "apollo-11")]:
    for body, code, offset in [("Sun", "10", 0), ("Earth", "399", 3)]:
        times, az_ref, el_ref = query(code, site["lat"], site["lon"], "2036-01-01", "2036-12-31", "30 d")
        hours = [int((t - start).total_seconds() / 3600) for t in times]
        az, el = altaz(vectors[hours, offset:offset+3].astype(np.float64), site["lat"], site["lon"], 0)
        daz = np.where(np.abs(el_ref) > 89, 0, np.abs(angle_diff(az, az_ref)))
        dele = np.abs(el - el_ref)
        result = {"site": site["id"], "body": body, "samples": len(times), "maxAzDifferenceDeg": float(daz.max()), "maxElDifferenceDeg": float(dele.max())}
        report.append(result)
        print(json.dumps(result), flush=True)
        assert daz.max() < 0.001 and dele.max() < 0.001
(output / "horizons-2036.json").write_text(json.dumps({"source": "https://ssd.jpl.nasa.gov/api/horizons.api", "year": 2036, "step": "30 d", "toleranceDeg": 0.001, "cases": report}, indent=2))
