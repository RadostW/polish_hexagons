import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the CSV file
#df = pd.read_csv("assigned_hexagons.csv")
df = pd.read_csv("optimized_assigned_hexagons.csv")

# Create the plot
plt.figure(figsize=(10, 10))

n_groups = 0

# Plot powiat centers
grouped = df.groupby("powiat_easting")
for name, group in grouped:
    n_groups = n_groups + 1

    powiat_easting = group["powiat_easting"].iloc[0]
    powiat_northing = group["powiat_northing"].iloc[0]
    
    #plt.scatter(powiat_easting, powiat_northing, color='green', s=50, label=f"Powiat: {name}")
    
    # Plot hexagon centers and draw connecting lines
    plt.scatter(group["hexagon_easting"], group["hexagon_northing"], s=10)
    
    mean_easting = np.mean(group["hexagon_easting"])
    mean_northing = np.mean(group["hexagon_northing"])

    alpha = 0.1
    if np.std(group["hexagon_easting"]) + np.std(group["hexagon_northing"]) > 10_000:
        alpha = 0.8
        # plt.scatter(powiat_easting, powiat_northing, s=50, label=f"Powiat: {name}")
        # for _, row in group.iterrows():
        #     plt.plot([powiat_easting, row["hexagon_easting"]],
        #          [powiat_northing, row["hexagon_northing"]],
        #          color='black', alpha=alpha)
        

    for _, row in group.iterrows():
        plt.plot([mean_easting, row["hexagon_easting"]],
                 [mean_northing, row["hexagon_northing"]],
                 color='gray', alpha=alpha)

print(f"number of regions {n_groups}")

# plt.legend()
plt.xlabel("Easting")
plt.ylabel("Northing")
plt.title("Powiat-Hexagon Assignments")
plt.show()
