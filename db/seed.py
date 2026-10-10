import datetime
import io
import uuid

import numpy as np
import pandas as pd

import config

"""NOTE: THIS DATA IS COMPLETELY FAKE BUT REALISTIC SO THE MODEL HAS INITIAL DATA TO LEARN FROM
This is a docstring explaining all the contents in the file:
Time: 28 days of data, ending 01.10.26 00:00:00 (UK fmt). Demand counted in 15-minute windows. Drivers ping every 3 minutes while on shift. Weekend means Saturday and Sunday.
Zones: (TOOK ME FOREVER TO FORMAT THIS, like 20 minutes 😭😭)
________________________________________________________________________________________________________________________________________________________________________
|    Name    |  Normal demand per 15 min  |  Peak demand  |             Peak hours            |      Weekend     |  Spike length  |  Cancel rate  |  Peak supply ratio |
|  Kristown  |             12             |     none      |            none (flat)            |	same as weekdays |	    90 min    |	     15%      |	        2.0        |
|  Susietown |              8             |      40       |	weekdays 4-6pm, smaller bump 8-9am|	     25% less    |	    60 min    |	     15%      |	        0.5        |
| Ralseitown |              8	          |      30	      |      weekdays 7-9am and 5-7pm     |	     15% more    |	    30 min    |	     10%      |	        0.6        |
| Noelletown | 3 weekdays, 10 weekend days|      35       |       Fri and Sat 10pm-2am        |	     15% more    |	   120 min    |    	 30%      |	        0.9        |
| Tennatown  |             25             |      35	      |      bursts 6-8am and 4-7pm       |	     the same    |	    15 min    |	     5%       |	        1.2        |
| Jeviltown	 |              8             |      15       |               5-8pm               |	     15% more    |	    10 min    |	     10%      |	        0.9        |
‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
Demand rule: Expected requests per window come from the zone's normal or peak level for that hour and day, then the actual count is drawn randomly around it. Overnight (1am to 5am) drops to about 10% everywhere except Noelletown's Friday and Saturday nights.
Spikes: 1 - 3 per zone per week, demand multiplied by 2x-4x
Drivers: There are 200, 50% on peak and 15% overnight, On a shift, they ping every 3 minutes usually from their home zone, zone shares are set so that peak supply:demand ratios land near the last list column, some are marked unavailable (more frequent during busy hours)
Ride Status: Ends in completed, cancelled or still requested, cancelled still counts as demand
Loading Rules: Fixed random seed from config.py. Clear the tables first so re-running is safe. Load zones, then rides and pings in bulk. Leave pricing_logs empty.
Checks after loading: Row counts per table. Peak hours appear where designed. Spike windows clearly exceed the zone's norm. Peak supply:demand ratios sit near the targets.
Map:
__________________________________________________________
|                  |                  |                  |
|                  |                  |                  |
|                  |                  |                  |
|     Kristown     |    Noelletown    |    Ralseitown    |
|                  |                  |                  |
|                  |                  |                  |
|__________________|__________________|__________________|
|                  |                  |                  |
|                  |                  |                  |
|                  |                  |                  |
|    Susietown     |    Tennatown     |    Jeviltown     |
|                  |                  |                  |
|                  |                  |                  |
|__________________|__________________|__________________|
"""

# Constants from config
seed = config.RANDOM_SEED
days = config.SEED_DAYS
end_date = config.SEED_END_DATE
driver_num = config.SEED_NUM_DRIVERS
demand_window_minutes = config.DEMAND_WINDOW_MINUTES
end_dt = datetime.datetime.fromisoformat(end_date)
start_dt = end_dt - datetime.timedelta(days=days)

# Dataframe of values and multiplier
zone_id = [1, 2, 3, 4, 5, 6]
zone = ["Kristown", "Susietown", "Ralseitown", "Noelletown", "Tennatown", "Jeviltown"]  # The 6 zones
weekday_demand = [12, 8, 8, 3, 25, 8]  # How many demands usually made per window per weekday
weekend_demand = [12, 6, 9, 10, 25, 9]  # How many demands usually made per window per weekend day
peak_demand = [12, 40, 30, 35, 35, 15]  # How many demands per window in peak time
spike_minute = [90, 60, 30, 120, 15, 10]  # How long a spike lasts for in minutes
cancel_rate = [0.15, 0.15, 0.10, 0.30, 0.05, 0.10]  # Chance of a demand being cancelled
target_ratio = [2.0, 0.5, 0.6, 0.9, 1.2, 0.9]  # Supply:Demand ratio at peak using available drivers
values_df = pd.DataFrame(
    {
        "zone_id": zone_id,
        "zone": zone,
        "weekday_demand": weekday_demand,
        "weekend_demand": weekend_demand,
        "peak_demand": peak_demand,
        "spike_minute": spike_minute,
        "cancel_rate": cancel_rate,
        "target_ratio": target_ratio,
    }
)  # Dataframe of these values

windows = pd.date_range(start=start_dt, end=end_dt, freq=f"{demand_window_minutes}min", inclusive="left") # All windows

# Dataframe of peaks, how do I begin to explain this 
peak_df = pd.DataFrame(
    {
        "zone_id": [2, 2, 3, 3, 4, 4, 4, 4, 5, 5, 6],
        "applies_to": ["weekday", "weekday", "weekday", "weekday", "fri", "sat", "sat", "sun", "all", "all", "all"],
        "start_hour": [16, 8, 7, 17, 22, 22, 0, 0, 6, 16, 17],
        "end_hour": [18, 9, 9, 19, 24, 24, 2, 2, 8, 19, 20],
        "level": [40, 20, 30, 30, 35, 35, 35, 35, 35, 35, 15],
    }
)

# Window zone Dataframe
wz_df = pd.MultiIndex.from_product([windows, values_df["zone"]], names=["window_start", "zone"]).to_frame() # Frame of windows, zone
zone_map = dict(zip(values_df["zone"], values_df["zone_id"])) # Dictionary of zone: id
wz_df["zone_id"] = wz_df["zone"].map(zone_map) # Creating zone id column
wz_df["hour"] = wz_df["window_start"].dt.hour # Creating hour column
wz_df["day_of_week"] = wz_df["window_start"].dt.day_of_week # Creating Day of week column
wz_df["is_weekend"] = wz_df["day_of_week"].isin([5, 6]) # Creating Boolean column of if day is weekend or not
wz_df["day_type"] = np.where(wz_df["is_weekend"], "weekend", "weekday") # Creating day type column (weekday/weekend)
wz_df["day_name"] = wz_df["window_start"].dt.strftime("%a").str.lower() # Creating day name column of day of the week 3 letter all lowercase format

seed = config.RANDOM_SEED # Getting seed from config
rng = np.random.default_rng(seed=seed) # Making numpy rng

all_zones = dict(zip(values_df["zone"], values_df["spike_minute"])) # Dictionary of zone: Spike length

# List of all spikes values
period_zone = [] # Zone names
spike_period_start = [] # Spike start time
spike_period_end = [] # Spike end time
spike_multiplier = [] # Spike multiplier

for town in values_df["zone"]: # Looping 6 zones
    slice_start = 0 # Slicing floor
    slice_end = 672 # Slicing ceiling
    for week in range(4): # Looping 4 weeks
        spike_len = all_zones[town] # Get spike length from all_zones dict
        week_pool = windows[slice_start:slice_end] # Get all periods in the week
        slice_start += 672 # Update floor
        slice_end += 672 # Update Ceiling
        spike_amount = rng.choice([1, 2, 3]) # Random number for amount of spikes
        for i in range(spike_amount): # Looping amount of spikes
            spike_period = rng.choice(week_pool) # Choose random time
            period_end = spike_period + datetime.timedelta(minutes=int(spike_len)) # Calculate time of spike ending
            multiplier = rng.uniform(2.0, 4.0) # Calculate random multiplier between x2 and x4
            multiplier = round(multiplier, 2) # Round to 2 d.p
            # Adding to columns
            period_zone.append(town)
            spike_period_start.append(spike_period)
            spike_period_end.append(period_end)
            spike_multiplier.append(multiplier)

spikes_df = pd.DataFrame({"period_zone": period_zone, "spike_start": spike_period_start, "spike_end": spike_period_end, "multiplier": spike_multiplier}) # Dataframe of the spikes data

wz_df = wz_df.reset_index(drop=True) # Reset index
wz_df = wz_df.merge(values_df[["zone", "weekday_demand", "weekend_demand"]], "left", "zone") # Add relevant data to wz_df
wz_df["expected"] = np.where(wz_df["is_weekend"], wz_df["weekend_demand"], wz_df["weekday_demand"]) # Create expected demand column
wz_df["expected"] = wz_df["expected"].astype(float) # Make expected a float column

# Dictionary of used applies to 
applies_to = {
    "all": [0, 1, 2, 3, 4, 5, 6],
    "weekday": [0, 1, 2, 3, 4],
    "fri": [4],
    "sat": [5],
    "sun": [6]
}

for index, row in peak_df.iterrows():
    # Targets the window is filtered by
    tar_zone = wz_df["zone_id"] == row["zone_id"]
    tar_start = wz_df["hour"] >= row["start_hour"]
    tar_end = wz_df["hour"] < row["end_hour"]
    tar_day = wz_df["day_of_week"].isin(applies_to[row["applies_to"]])
    matches = tar_zone & tar_start & tar_end & tar_day # Final check
    wz_df.loc[matches, "expected"] = row["level"] # Select true row of each expected and make it level
    overnight = (wz_df["hour"] >= 1) & (wz_df["hour"] < 5) # Get overnight hours
    is_noelletown = wz_df["zone_id"] == 4 # See if current town is noelletown
    is_weekend_night = wz_df["day_of_week"].isin([5, 6]) # Check if weekend
    exempt = is_noelletown & is_weekend_night # Except noelletown
    to_reduce = ~exempt & overnight # Inverse values in the bool column and compare if overnight
wz_df.loc[to_reduce, "expected"] *= 0.1
wz_df["window_end"] = wz_df["window_start"] + pd.Timedelta(minutes=demand_window_minutes) # Window end timedelta

for index, row in spikes_df.iterrows(): # Iterate spikes df
    # Targets the spike is filtered by
    tar_period = wz_df["zone"] == row["period_zone"]
    tar_start = wz_df["window_start"] < row["spike_end"]
    tar_end = wz_df["window_end"] > row["spike_start"]
    spike_matches = tar_period & tar_start & tar_end # Final check
    wz_df.loc[spike_matches, "expected"] *= row["multiplier"] # Multiply the window to meet spike demand