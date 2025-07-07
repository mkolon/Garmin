# analyze_hr_source.py

from fitparse import FitFile
import pandas as pd
import sys

def identify_hr_source(device_info):
    """Determine HR source: chest strap or watch."""
    hr_sources = set()
    for d in device_info:
        src = d.get("source_type")
        if src in ("antplus", "bluetooth"):
            hr_sources.add("external")
        elif src == "local":
            hr_sources.add("watch")
    return hr_sources

if len(sys.argv) != 2:
    print("Usage: python analyze_hr_source.py <your_fit_file.fit>")
    sys.exit(1)

fit_path = sys.argv[1]
fitfile = FitFile(fit_path)

# Extract device info
device_info = []
for record in fitfile.get_messages("device_info"):
    device_info.append({d.name: d.value for d in record})

# Determine HR source
sources = identify_hr_source(device_info)
print("\n=== HR Source Analysis ===")
if "external" in sources:
    print("✔ Heart rate was recorded using a chest strap (ANT+ or Bluetooth).")
elif "watch" in sources:
    print("⚠ Heart rate was recorded using the watch's built-in optical sensor.")
else:
    print("✖ No heart rate source could be identified.")


