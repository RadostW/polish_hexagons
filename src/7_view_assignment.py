import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file
df = pd.read_csv("assigned_hexagons.csv")

# Create the plot
plt.figure(figsize=(10, 10))

# Plot powiat centers
grouped = df.groupby("name")
for name, group in grouped:
    powiat_easting = group["powiat_easting"].iloc[0]
    powiat_northing = group["powiat_northing"].iloc[0]
    
    plt.scatter(powiat_easting, powiat_northing, color='green', s=50, label=f"Powiat: {name}")
    
    # Plot hexagon centers and draw connecting lines
    plt.scatter(group["hexagon_easting"], group["hexagon_northing"], color='red', s=10)
    for _, row in group.iterrows():
        plt.plot([row["powiat_easting"], row["hexagon_easting"]],
                 [row["powiat_northing"], row["hexagon_northing"]],
                 color='gray', alpha=0.5)

plt.xlabel("Easting")
plt.ylabel("Northing")
plt.title("Powiat-Hexagon Assignments")
plt.show()
