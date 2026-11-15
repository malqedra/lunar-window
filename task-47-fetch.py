import sys
from pathlib import Path

sys.path.insert(0, str(Path(sys.argv[1]) / "pipeline"))
from fetch_data import RAW, FILES, fetch

RAW.mkdir(parents=True, exist_ok=True)
for name in ("de421.bsp", "moon_pa_de421_1900-2050.bpc", "moon_080317.tf"):
    fetch(name, *FILES[name])
