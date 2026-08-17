import csv
from pathlib import Path


# Get the main project folder.
# load_data.py is inside src/,
# so parent.parent moves us back to dataguard/.
PROJECT_ROOT = Path(__file__).parent.parent


# Build the path to our CSV file.
DATA_FILE = PROJECT_ROOT / "data" / "customers.csv"


print("DataGuard - Dataset Loader")
print("-" * 40)

print(f"Dataset path: {DATA_FILE}")


# Open the CSV file.
with open(DATA_FILE, mode="r", newline="", encoding="utf-8") as file:

    reader = csv.DictReader(file)

    rows = list(reader)


print(f"Number of rows: {len(rows)}")

print(f"Columns: {reader.fieldnames}")

print("\nFirst 3 records:")

for row in rows[:3]:
    print(row)
