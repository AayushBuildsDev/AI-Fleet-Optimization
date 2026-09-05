import csv
import random
import os

random.seed(42)

output_path =  "data/raw/fleet_history.csv"

os.makedirs("data/raw", exist_ok=True)

rows = []

for i in range(1, 1001):

    # Trip information
    distance_km = random.randint(50, 1200)
    load_weight_kg = random.randint(500, 19000)
    fuel_efficiency_kmpl = round(random.uniform(5.5, 10.0), 2)
    average_speed_kmh = round(random.uniform(30, 80), 2)

    # Base fuel consumption
    base_fuel = distance_km / fuel_efficiency_kmpl

    # Heavier loads increase fuel consumption
    load_factor = 1 + (load_weight_kg / 20000) * 0.20

    # Higher speed slightly increases consumption
    speed_factor = 1 + max(0, average_speed_kmh - 50) / 500

    # Small random variation
    noise_factor = random.uniform(0.95, 1.05)

    fuel_used_liters = (
        base_fuel
        * load_factor
        * speed_factor
        * noise_factor
    )

    rows.append([
        i,
        distance_km,
        load_weight_kg,
        fuel_efficiency_kmpl,
        average_speed_kmh,
        round(fuel_used_liters, 2)
    ])


with open(output_path, "w", newline="") as file:

    writer = csv.writer(file)

    writer.writerow([
        "trip_id",
        "distance_km",
        "load_weight_kg",
        "fuel_efficiency_kmpl",
        "average_speed_kmh",
        "fuel_used_liters"
    ])

    writer.writerows(rows)


print("Historical fleet dataset created successfully!")
print(f"Records created: {len(rows)}")
print(f"File: {output_path}")