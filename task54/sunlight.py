"""Hourly 2026 north illumination map using committed field and ephemeris."""
import gzip
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "pipeline"))
from build_field import grid_centers
import engine
from horizon import altaz, disc_fraction, horizon_at, local_frame
from terrain import Terrain, to_latlon, to_map

OUT = Path(__file__).resolve().parent
DATA = ROOT / "web/public/data"
n, x, y = grid_centers(40000, 250)
lat, lon = to_latlon(x.ravel(), y.ravel(), "north")
up, east, north = local_frame(lat, lon)
sun = np.fromfile(DATA / "ephem.bin", dtype="<f4").reshape(-1, 6)[:8760, :3].astype(float)
d = np.frombuffer(gzip.decompress((DATA / "field_north.bin.gz").read_bytes()), dtype=np.uint8).reshape(180, n, n)
h = ((np.cumsum(d, axis=0) % 256) * 0.1 - 8).transpose(1, 2, 0).reshape(n * n, 180)
ground = Terrain("north").height_xy(x.ravel(), y.ravel())
cached = "--plot-only" in sys.argv
mean = np.load(OUT / "sunlit-2026.npy").ravel() if cached else np.zeros(n * n)
for start in ([] if cached else range(0, n * n, 256)):
    end = min(start + 256, n * n)
    # Exact topocentric projections: the observer displacement only subtracts
    # from the local-up component. East/north remain dot products in ME.
    e = east[start:end] @ sun.T
    no = north[start:end] @ sun.T
    u = up[start:end] @ sun.T - ((1737400 + ground[start:end] + 2) / 1000)[:, None]
    el = np.degrees(np.arctan2(u, np.hypot(e, no)))
    az = np.mod(np.degrees(np.arctan2(e, no)), 360) / 2
    a = np.floor(az).astype(int)
    w = az - a
    rows = np.arange(end - start)[:, None]
    skyline = h[start:end][rows, a] * (1 - w) + h[start:end][rows, (a + 1) % 180] * w
    mean[start:end] = disc_fraction(el - skyline).mean(axis=1) * 100
    if start % 8192 == 0:
        print(f"illumination {end}/{n*n}", flush=True)
mean = mean.reshape(n, n)
np.save(OUT / "sunlit-2026.npy", mean)

# Glaser et al., 2018, Tables 1/2, Peary rim coordinates at surface / 2 m.
# https://ntrs.nasa.gov/citations/20170007365
sites = {"Peary rim P": (89.7260, 123.11), "Peary rim P0 (2 m)": (89.8521, 109.80)}
stats = {}
for label, (p, l) in sites.items():
    sx, sy = to_map(p, l, "north")
    row, col = int((40000 - sy) // 250), int((sx + 40000) // 250)
    local = mean[np.hypot(x - sx, y - sy) <= 1000]
    stats[label] = {"lat": p, "lon": l, "cell_percent": float(mean[row, col]),
                    "best_within_1km_percent": float(local.max()),
                    "best_within_1km_percentile": float((mean <= local.max()).mean() * 100)}
stats["Peary rim P"]["cell_percentile"] = float((mean <= stats["Peary rim P"]["cell_percent"]).mean() * 100)
# The task asks that the rim be one of the brightest areas, not that a 250 m
# grid reproduce the study's 20 m peaks or its different 20-year time window.
assert stats["Peary rim P"]["cell_percentile"] > 99
stats["map"] = {"year": 2026, "hourly_samples": len(sun), "points": n*n,
                "median_percent": float(np.median(mean)), "max_percent": float(mean.max())}
terrain = Terrain("north")
for label, (p, l) in sites.items():
    skyline = engine.horizon(p, l, 720, hemisphere="north")[0]
    az, el = altaz(sun, p, l, float(terrain.height(p, l)) + 2)
    stats[label]["exact_point_720_direction_percent"] = float(disc_fraction(el - horizon_at(skyline, az)).mean() * 100)
(OUT / "sunlight-checks.json").write_text(json.dumps(stats, indent=2) + "\n")
print(json.dumps(stats, indent=2))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(9, 8), layout="constrained")
im = ax.imshow(mean, extent=(-40, 40, -40, 40), origin="upper", cmap="inferno", vmin=0, vmax=100)
for label, (p, l) in sites.items():
    sx, sy = to_map(p, l, "north")
    ax.plot(sx / 1000, sy / 1000, "o", ms=6, mec="white", mfc="none")
    ax.annotate(label, (sx/1000, sy/1000), xytext=(-24, 10) if "P0" in label else (11, -7),
                color="white", fontsize=9, bbox={"facecolor": "black", "alpha": 0.6, "edgecolor": "none"},
                arrowprops={"arrowstyle": "-", "color": "white"})
ax.plot(0, 0, "+", color="cyan", ms=10)
ax.set(xlabel="Polar map x (km)", ylabel="Polar map y (km; +y toward longitude 180°)",
       title="North pole · mean visible Sun disc in 2026\nHourly samples · 250 m cells · observer 2 m")
fig.colorbar(im, ax=ax, label="Mean visible Sun disc (%)")
fig.savefig(OUT / "north-sunlight-2026.png", dpi=150)
plt.close(fig)
