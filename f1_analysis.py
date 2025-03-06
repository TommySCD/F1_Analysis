import fastf1
import fastf1.plotting
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import numpy as np
import gui
import seaborn as sns
from collections import defaultdict

# Define team colors
TEAM_COLORS = {
    "Mercedes": "#6CD3BF",
    "Red Bull Racing": "#1E41FF",
    "Ferrari": "#DC0000",
    "McLaren": "#FF8700",
    "Aston Martin": "#358C75",
    "Alpine": "#2293D1",
    "Williams": "#37BEDD",
    "Haas F1 Team": "#B6BABD",
    "Kick Sauber": "#52E252",
    "RB": "#5E8FAA",
    "Renault": "#FFF500",
    "Racing Point": "#F596C8",
    "Toro Rosso": "#469BFF",
    "Force India": "#FF80C7",
    "BMW Sauber": "#FFFFFF",
    "Lotus": "#FFB800",
    "Toyota": "#E4002B",
    "Alfa Romeo Racing": "#900000",
    "Alfa Romeo": "#900000",
    "AlphaTauri": "#2B4562"
}


# Load F1 session data dynamically from GUI selections
def load_session(mode, year, grand_prix, session_type):
    if mode == "Grand Prix":
        session_mapping = {
            "FP1": "FP1",
            "FP2": "FP2",
            "FP3": "FP3",
            "Qualifying": "Qualifying",
            "Race": "Race"
        }
        if not all([year, grand_prix, session_type]):
            return None
        try:
            session = fastf1.get_session(int(year), grand_prix, session_mapping[session_type])
            session.load()
            return session
        except Exception as e:
            print(f"Error loading session: {e}")
            return None
    return None

'''------------------------------------------------------------------------------------'''

'''RACE PLOTS'''

# Plot 1: Stint comparison between drivers
def plot_stint_comparison(session, drivers, team_colors):

    plt.style.use("dark_background")
    plt.figure(figsize=(12, 6), dpi=100)
    
    driver_positions = {}
    pit_lap_counts = defaultdict(int)  # Track how many pit stops happened on each lap
    
    for driver in drivers:
        laps = session.laps.pick_drivers(driver)

        team = laps.iloc[0]["Team"]  
        color = team_colors.get(team, "white")  
        final_position = laps.iloc[-1]["Position"]  
        pit_stops = laps["PitInTime"].count()
        driver_positions[driver] = final_position

        # Get lap numbers and valid lap times
        valid_laps = laps.dropna(subset=["LapTime"])
        valid_laps = valid_laps[~valid_laps["PitInTime"].notna()]  # Remove in-laps
        valid_laps = valid_laps[~valid_laps["PitOutTime"].notna()]  # Remove out-laps

        lap_numbers = valid_laps["LapNumber"].values
        lap_times = valid_laps["LapTime"].dt.total_seconds().values
        
        # Filter out unrealistic lap times (e.g., greater than 200s)
        lap_times = np.where((lap_times > 200), np.nan, lap_times)

        # Identify pit exit laps
        pit_exit_laps = laps[laps["PitOutTime"].notna()]["LapNumber"].values

        # Remove first recorded lap if it's a pit exit (start from the pit lane)
        if pit_exit_laps.size > 0 and pit_exit_laps[0] == 1:
            pit_exit_laps = pit_exit_laps[1:]           
        
        # Plot stint comparison
        plt.plot(lap_numbers, lap_times, color=color, linewidth=2, label=f"{driver} P{int(final_position)}, {pit_stops} stop")

        # Mark pit exit laps with vertical dashed lines
        offset = 0.15  # offset to separate overlapping lines
        for pit_exit in pit_exit_laps:
            pit_lap_counts[pit_exit] += 1  # Count pit stops on this lap
            shift = (pit_lap_counts[pit_exit] - 1) * offset  # Adjust position
            
            plt.axvline(x=pit_exit + shift, color=color, linestyle=":", alpha=0.8, linewidth=1)

    # Titles & Labels
    driver_info = " vs ".join([f"{driver} (P{int(pos)})" for driver, pos in driver_positions.items()])
    plt.xlabel("Lap Number")
    plt.ylabel("Lap Time (s)")
    plt.title(f"{session.event['EventName']} {session.event.year} {session.name} - Stint Comparison \n"
              f"{driver_info}")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.show()

# Plot 2: Lap time distribution
def plot_lap_time_distribution(session):
    plt.style.use("dark_background")
    
    laps = session.laps.pick_quicklaps()
    transformed_laps = laps.copy()
    transformed_laps.loc[:, "LapTime (s)"] = laps["LapTime"].dt.total_seconds()
    team_order = (
        transformed_laps[["Team", "LapTime (s)"]]
        .groupby("Team")
        .median()["LapTime (s)"]
        .sort_values()
        .index
    )
    print(team_order)

    team_palette = {team: fastf1.plotting.get_team_color(team, session)
                    for team in team_order}

    fig, ax = plt.subplots(figsize=(12, 6), dpi=100)
    
    sns.boxplot(
        data=transformed_laps,
        x="Team",
        y="LapTime (s)",
        hue="Team",
        order=team_order,
        palette=team_palette,
        whiskerprops=dict(color="white"),
        boxprops=dict(edgecolor="white"),
        medianprops=dict(color="grey"),
        capprops=dict(color="white"),
    )

    plt.title(f"{session.event['EventName']} {session.event.year} {session.name}\n"
              f"Lap Time Distribution")
    plt.grid(True, linestyle="--", alpha=0.5)

    ax.set(xlabel=None)
    plt.tight_layout()
    plt.show()

'''--------------------------------------------------------------------'''

'''QUALIFYING PLOTS'''

# Plot 1: Best Lap per Team in Qualifying
def plot_best_laps(session):
    plt.style.use("dark_background") 

    fastest_laps = session.laps.loc[session.laps.groupby("Team")["LapTime"].idxmin()]
    fastest_laps = fastest_laps.sort_values("LapTime")

    teams = fastest_laps["Team"]
    delta_time = (fastest_laps["LapTime"] - fastest_laps["LapTime"].min()).dt.total_seconds()
    
    # Get best lap time and driver
    best_lap_time = fastest_laps["LapTime"].min()
    best_driver = fastest_laps.loc[fastest_laps["LapTime"].idxmin(), "Driver"]

    # Format time to m:ss.sss
    total_seconds = best_lap_time.total_seconds()
    formatted_time = f"{int(total_seconds // 60)}:{total_seconds % 60:06.3f}"  

    plt.figure(figsize=(10, 6), dpi=100) 

    # Use team colors
    colors = [TEAM_COLORS.get(team, "gray") for team in teams]

    plt.barh(teams, delta_time, color=colors)
    plt.xlabel("Delta Time (s)")
    plt.ylabel("Team")
    plt.title("Best Lap Time Per Team")
    plt.gca().invert_yaxis()
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.suptitle(
        f"{session.event['EventName']} {session.event.year} {session.name}\n"
        f"Fastest Lap: {best_driver} {formatted_time}\n",
        fontsize=10,
        color="lightgray"
    )
    plt.show()

# Plot 2: Lap comparison between two drivers
def plot_lap_comparison(session, driver1, driver2):
    plt.style.use("dark_background")

    # Get fastest lap telemetry for both drivers
    lap1 = session.laps.pick_drivers(driver1).pick_fastest().get_telemetry()
    lap2 = session.laps.pick_drivers(driver2).pick_fastest().get_telemetry()

    # Ensure "Distance" is included in telemetry
    lap1 = lap1.add_distance()
    lap2 = lap2.add_distance()

    # Get driver team colors dynamically
    driver1_team = session.laps.pick_drivers(driver1).iloc[0]["Team"]
    driver2_team = session.laps.pick_drivers(driver2).iloc[0]["Team"]
    
    color1 = TEAM_COLORS.get(driver1_team, "gray")
    color2 = TEAM_COLORS.get(driver2_team, "gray")

    # Find the fastest lap between the two drivers
    driver_laps = session.laps[session.laps["Driver"].isin([driver1, driver2])]
    fastest_lap = driver_laps.loc[driver_laps["LapTime"].idxmin()]

    best_lap_time = fastest_lap["LapTime"]
    best_driver = fastest_lap["Driver"]

    # Format time to m:ss.sss
    total_seconds = best_lap_time.total_seconds()
    formatted_time = f"{int(total_seconds // 60)}:{total_seconds % 60:06.3f}"  

    fig, axs = plt.subplots(3, 1, figsize=(12, 10), dpi=100)

    # Speed comparison
    axs[0].plot(lap1["Distance"], lap1["Speed"], label=driver1, color=color1)
    axs[0].plot(lap2["Distance"], lap2["Speed"], label=driver2, color=color2)
    axs[0].set_ylabel("Speed (km/h)")
    axs[0].legend()
    axs[0].grid(True, linestyle="--", alpha=0.5)

    # Throttle comparison
    axs[1].plot(lap1["Distance"], lap1["Throttle"], label=driver1, color=color1)
    axs[1].plot(lap2["Distance"], lap2["Throttle"], label=driver2, color=color2)
    axs[1].set_ylabel("Throttle (%)")
    axs[1].grid(True, linestyle="--", alpha=0.5)

    # Convert Timedelta to total seconds
    lap2_time_seconds = lap2["Time"].dt.total_seconds()
    lap1_time_seconds = lap1["Time"].dt.total_seconds()

    # Interpolate lap2's time onto lap1's distance
    lap2_time_interpolated = np.interp(lap1["Distance"], lap2["Distance"], lap2_time_seconds)

    # Compute time gap
    time_gap = lap1_time_seconds - lap2_time_interpolated

    # Plot time gap instead of speed difference
    axs[2].plot(lap1["Distance"], time_gap, color="white")
    axs[2].set_ylabel(f"{driver1} vs {driver2}")
    axs[2].axhline(0, color="gray", linestyle="--", alpha=0.7)
    axs[2].grid(True, linestyle="--", alpha=0.5)

    plt.xlabel("Distance (m)")
    plt.suptitle(
        f"{session.event['EventName']} {session.event.year} {session.name} \n"
        f"Lap Comparison: {driver1} vs {driver2}\n"
        f"Fastest Lap Between Them: {best_driver} {formatted_time}\n"
    )
    plt.show()


# Plot 3: Maximum Speeds Compared to Best Lap Times
def plot_max_speeds(session):
    drivers = session.laps["Driver"].unique()
    max_speeds = {}
    best_laps = {}
    team_colors = {}

    for driver in drivers:
        laps = session.laps.pick_drivers(driver)
        max_speeds[driver] = laps["SpeedST"]
        best_laps[driver] = laps.pick_fastest()["LapTime"]
        
        # Get team color dynamically
        team = laps.iloc[0]["Team"]
        team_colors[driver] = TEAM_COLORS.get(team, "gray")

    delta_times = [(best_laps[drv] - min(best_laps.values())).total_seconds() for drv in drivers]
    speeds = [max_speeds[drv].max() for drv in drivers]
    colors = [team_colors[drv] for drv in drivers] 

    plt.figure(figsize=(10, 6), dpi=100)
    plt.scatter(delta_times, speeds, color=colors, edgecolors="white", s=100) 

    for drv, x, y, color in zip(drivers, delta_times, speeds, colors):
        plt.text(x, y, drv, fontsize=9, color=color, ha="left", va="bottom")

    plt.xlabel("Delta Time (s)")
    plt.ylabel("Top Speed (km/h)")
    plt.title(f"{session.event['EventName']} {session.event.year} {session.name} - Maximum Speeds vs Best Lap Time")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.style.use("dark_background")
    plt.show()


if __name__ == "__main__":
    gui.run_gui()
