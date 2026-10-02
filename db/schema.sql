-- Table for Rider info
CREATE TABLE if not EXISTS rider(
    ride_id UUID PRIMARY KEY,
    rider_id UUID NOT NULL,
    pickup_zone_id UUID INT NOT NULL
    dropoff_zone_id UUID INT NOT NULL
    distance_miles NUMERIC(5, 2) NOT NULL
    status VARCHAR(20) NOT NULL, -- Permitted statuses: 'requested', 'completed', 'cancelled'
    requested_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Table for GPS Telemetrics from active drivers
CREATE TABLE IF NOT EXISTS driver_locations (
    ping_id BIGSERIAL PRIMARY KEY,
    driver_id UUID NOT NULL,
    zone_id INT NOT NULL,
    is_available BOOLEAN NOT NULL DEFAULT TRUE,
    ping_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Audits of dynamic prices generated
CREATE TABLE IF NOT EXISTS pricing_logs (
    log_id BIGSERIAL PRIMARY KEY,
    ride_id UUID REFERENCES rides(ride_id),
    base_fare NUMERIC(6, 2) NOT NULL,
    surge_multiplier NUMERIC(3, 2) NOT NULL,
    final_fare NUMERIC(6, 2) NOT NULL,
    calculated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);