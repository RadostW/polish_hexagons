import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import distance
from tqdm import tqdm

# Load CSV file
df = pd.read_csv("assigned_hexagons.csv")


# Compute squared distance for a single assignment
def compute_squared_distance(row):
    return (row["powiat_easting"] - row["hexagon_easting"]) ** 2 + (
        row["powiat_northing"] - row["hexagon_northing"]
    ) ** 2


def plot_assignment(df, iteration):
    plt.figure(figsize=(10, 10))
    grouped = df.groupby("name")
    for name, group in grouped:
        powiat_easting = group["powiat_easting"].iloc[0]
        powiat_northing = group["powiat_northing"].iloc[0]

        plt.scatter(
            powiat_easting,
            powiat_northing,
            color="green",
            s=50,
            label=f"Powiat: {name}",
        )
        plt.scatter(
            group["hexagon_easting"], group["hexagon_northing"], color="red", s=10
        )
        for _, row in group.iterrows():
            plt.plot(
                [row["powiat_easting"], row["hexagon_easting"]],
                [row["powiat_northing"], row["hexagon_northing"]],
                color="gray",
                alpha=0.5,
            )

    plt.xlabel("Easting")
    plt.ylabel("Northing")
    plt.title(f"Powiat-Hexagon Assignments (Iteration {iteration})")
    plt.savefig(f"iteration_{iteration}.pdf")
    plt.close()


def improve_assignment(df):
    made_improvement = True
    iteration = 0
    improve_count = 0

    plot_assignment(df, iteration)

    while made_improvement:
        made_improvement = False
        iteration = iteration + 1

        # for index1, row1 in tqdm(
        #     reversed(list(df.iterrows())),
        #     total=len(list(df.iterrows())),
        #     desc=f"Iteration {iteration}",
        # ):
        #     for index2, row2 in reversed(list(df.iterrows())):
        #         if index1 >= index2 or row1["name"] == row2["name"]:
        #             continue  # Skip same powiat or duplicate pairs

        for index1 in tqdm(reversed(range(len(df))), total=len(df), desc=f"Iteration {iteration}"):            
            for index2 in reversed(range(index1 + 1, len(df))):  # index2 starts from index1 + 1 to avoid repeats
                row1 = df.iloc[index1] # reassign because rows change
                row2 = df.iloc[index2]

                # Compute original distances
                original_dist1_sq = compute_squared_distance(row1)
                original_dist2_sq = compute_squared_distance(row2)
                original_dist1 = np.sqrt(original_dist1_sq)
                original_dist2 = np.sqrt(original_dist2_sq)

                # Swap hexagons
                new_row1 = row1.copy()
                new_row2 = row2.copy()
                new_row1[["hexagon_easting", "hexagon_northing"]] = row2[
                    ["hexagon_easting", "hexagon_northing"]
                ].values
                new_row2[["hexagon_easting", "hexagon_northing"]] = row1[
                    ["hexagon_easting", "hexagon_northing"]
                ].values

                # Compute new distances
                new_dist1_sq = compute_squared_distance(new_row1)
                new_dist2_sq = compute_squared_distance(new_row2)
                new_dist1 = np.sqrt(new_dist1_sq)
                new_dist2 = np.sqrt(new_dist2_sq)

                # Compute difference in total distance (in km)
                diff_km = (
                    (original_dist1 + original_dist2) - (new_dist1 + new_dist2)
                ) / 1000

                # If swap improves the total squared distance, apply it
                if (new_dist1_sq + new_dist2_sq) < (
                    original_dist1_sq + original_dist2_sq
                ):
                    df.loc[index1, ["hexagon_easting", "hexagon_northing"]] = new_row1[
                        ["hexagon_easting", "hexagon_northing"]
                    ].values
                    df.loc[index2, ["hexagon_easting", "hexagon_northing"]] = new_row2[
                        ["hexagon_easting", "hexagon_northing"]
                    ].values
                    print(
                        f"{row1['name']}-{row2['name']} : "
                        f"{original_dist1/1000:.2f}-{original_dist2/1000:.2f} -> "
                        f"{new_dist1/1000:.2f}-{new_dist2/1000:.2f} | "
                        f"Δ {diff_km:.3f} km"
                    )
                    made_improvement = True
                    improve_count = improve_count + 1                    

                    if(improve_count % 500 == 0):
                        print("=====")
                        print("Preview saved!")
                        print("=====")
                        plot_assignment(df, iteration)

                    duplicated = df[["hexagon_easting", "hexagon_northing"]].duplicated()

                    if df[["hexagon_easting", "hexagon_northing"]].duplicated().any():
                        print("ERROR!")

                        print(df[duplicated])
                        return

        # Save plot and CSV after each iteration
        plot_assignment(df, iteration)
        df.to_csv(f"optimized_assigned_hexagons_iteration_{iteration}.csv", index=False)

    return df


# Optimize assignments
df = improve_assignment(df)

# Save final optimized CSV
df.to_csv("optimized_assigned_hexagons.csv", index=False)
print("Optimized assignments saved to 'optimized_assigned_hexagons.csv'.")
