from pathlib import Path

import pydantic_settings
from pydantic import SecretStr

# Constants
DEMAND_WINDOW_MINUTES = 15
HISTORY_WEEKS = 4
MAX_DRIVER_PING_TIME_MINUTES = 5

BASE_FARE_FLAT = 3.00
RATE_PER_MILE = 1.80
MINIMUM_FARE = 5.00
MONEY_DECIMALS = 2

SURGE_FLOOR = 1.0
SURGE_CAP = 3.0

RATIO_SMOOTHING = 1.0
HISTORICAL_AVG_FLOOR = 1.0
NEUTRAL_SPIKE_INDEX = 1.0

AVG_SPEED_MPH = 20
DEFAULT_PICKUP_MINUTES = 10

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = f"{BASE_DIR}/models/surge_model.joblib"
RANDOM_SEED = 42
VALIDATION_FRACTION = 0.2
FEATURE_COLUMNS = ("recent_requests", "available_drivers", "supply_demand_ratio", "demand_spike_index", "log_distance", "hour", "day_of_week", "is_weekend")

SEED_DAYS = 28
SEED_NUM_DRIVERS = 200

class Settings(pydantic_settings.BaseSettings):
    model_config = pydantic_settings.SettingsConfigDict(env_file=f"{BASE_DIR}/.env", env_file_encoding="utf-8", extra="ignore")
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: SecretStr
    test_db_name: str

settings = Settings(_env_file=f"{BASE_DIR}/.env", _env_file_encoding="utf-8")

print(settings)