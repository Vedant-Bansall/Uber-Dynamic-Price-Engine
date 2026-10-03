-- Zone Location Table
CREATE TABLE IF NOT EXISTS zones (
    zone_id INT PRIMARY KEY,
    zone_name VARCHAR(50) NOT NULL
);

-- Table for Rides info
CREATE TABLE IF NOT EXISTS rides(
    ride_id UUID PRIMARY KEY,
    rider_id UUID NOT NULL,
    pickup_zone_id INT NOT NULL REFERENCES zones(zone_id),
    dropoff_zone_id INT NOT NULL REFERENCES zones(zone_id),
    distance_miles NUMERIC(5, 2) NOT NULL,
    status VARCHAR(20) NOT NULL,
    CONSTRAINT chk_status CHECK (status in ('requested', 'completed', 'cancelled')),  -- Permitted statuses: 'requested', 'completed', 'cancelled'
    requested_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Table for GPS Telemetrics from active drivers
CREATE TABLE IF NOT EXISTS driver_locations (
    ping_id BIGSERIAL PRIMARY KEY,
    driver_id UUID NOT NULL,
    zone_id INT NOT NULL REFERENCES zones(zone_id),
    is_available BOOLEAN NOT NULL DEFAULT TRUE,
    ping_time TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Audits of dynamic prices generated
CREATE TABLE IF NOT EXISTS pricing_logs (
    log_id BIGSERIAL PRIMARY KEY,
    ride_id UUID REFERENCES rides(ride_id),
    base_fare NUMERIC(6, 2) NOT NULL,
    surge_multiplier NUMERIC(3, 2) NOT NULL,
    final_fare NUMERIC(6, 2) NOT NULL,
    calculated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_rides_zone_time ON rides (pickup_zone_id, requested_at);
CREATE INDEX IF NOT EXISTS idx_pings_zone_time ON driver_locations (zone_id, ping_time);