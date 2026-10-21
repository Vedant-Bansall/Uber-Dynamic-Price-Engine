import numpy as np
import pandas as pd


def calculate_features(rides_df: pd.DataFrame) -> pd.DataFrame: # Function to make calculations of features
    df = rides_df.copy() # Copy of the rides df
    df["day_of_week"] = rides_df["requested_at"].dt.day_of_week # Day of week creation from requested at in the rides_df
    df["hour"] = df["requested_at"].dt.hour # Hour of requested_at
    df["is_weekend"] = df["day_of_week"].isin([5, 6]) # Checking if it is weekday
    df["log_distance"] = np.log1p(rides_df["distance_miles"].astype(float)) # Log distance of the distance_miles
    return df # Return edited DF