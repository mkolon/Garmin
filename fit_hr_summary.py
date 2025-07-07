# fit_hr_summary.py

from fitparse import FitFile
import pandas as pd
import sys

if len(sys.argv) != 2:
    print("Usage: python fit_hr_summary.py <your_fit_file.fit>")
    sys.exit(1)

fit_path = sys.argv[1]
fitfile = FitFile(fit_path)

# Extract device info
device_info = []
for record in fitfile.get_messages("device_info"):
    device_info.append({d.name: d.value for d in record})

# Show device info
if device_info:
    print("\n=== Device Info ===")
    for d in device_info:
        print({k: v for k, v in d.items() if k in ('manufacturer', 'product', 'serial_number', 'source_type')})
else:
    print("No device info found.")

# Extract heart rate data
hr_data = []
for record in fitfile.get_messages("record"):
    values = {d.name: d.value for d in record}
    if "heart_rate" in values:
        hr_data.append(values["heart_rate"])

# Show HR stats
if hr_data:
    hr_series = pd.Series(hr_data)
    print("\n=== Heart Rate Summary ===")
    print(hr_series.describe())
else:
    print("No heart rate data found.")

