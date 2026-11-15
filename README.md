# Ephemeris extension verification

Evidence for implementation commit `445280a950fc08a898aafad379a7335000c4f6ef`, based on upstream `515b6b0`.

Read [verification.md](verification.md) for the checks, results, and limits. `before-endpoint.jpg` and `after-endpoint.jpg` show the original and extended date limits. The six `year-2036-*.jpg` files show annual overlays. The finder and landing-date screenshots cover planning tools near the new end of the data.

The Python helpers reproduce the data checks without modifying the app:

```
python task-47-verify.py <implementation-checkout> <baseline-data-directory> <results-directory>
python task-47-horizons.py <implementation-checkout> <results-directory>
```

The baseline directory contains `ephem.bin`, `ephem.json`, and `dsn.bin` from `web/public/data` at `515b6b0`. The helpers require NumPy; the Horizons helper also imports the repository's pipeline modules and requires Skyfield and network access to NASA JPL. `task-47-fetch.py <checkout>` downloads only the three kernels needed by the existing ephemeris generator, using the repository's existing download URLs and size checks. Raw kernels are excluded from this record.
