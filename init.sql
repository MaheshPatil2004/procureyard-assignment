-- 1. Core Data Tables (Sourced from CSVs)
CREATE TABLE riders (
    rider_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100),
    phone_number VARCHAR(20)
);

CREATE TABLE trips (
    trip_id VARCHAR(50) PRIMARY KEY,
    rider_id VARCHAR(50) REFERENCES riders(rider_id),
    date DATE,
    distance_km DECIMAL(5,2),
    status VARCHAR(20), -- 'completed', 'cancelled', 'customer_cancelled'
    surge_multiplier DECIMAL(3,2) DEFAULT 1.0
);

CREATE TABLE payout_lines (
    id SERIAL PRIMARY KEY,
    rider_id VARCHAR(50) REFERENCES riders(rider_id),
    date DATE,
    amount DECIMAL(10,2)
);

-- 2. Idempotency & Conversational Memory
CREATE TABLE conversations (
    message_id VARCHAR(100) PRIMARY KEY, -- Enforces idempotency (prevents 10-second retry duplication)
    rider_id VARCHAR(50) REFERENCES riders(rider_id),
    text TEXT,
    role VARCHAR(20), -- 'user' or 'agent'
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Ops Portal Escalations & Agent Traces
CREATE TABLE agent_traces (
    id SERIAL PRIMARY KEY,
    rider_id VARCHAR(50) REFERENCES riders(rider_id),
    action_log JSONB, -- Stores the step-by-step tool calls
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE pending_approvals (
    id SERIAL PRIMARY KEY,
    rider_id VARCHAR(50) REFERENCES riders(rider_id),
    disputed_date DATE,
    requested_amount DECIMAL(10,2),
    reason TEXT,
    status VARCHAR(20) DEFAULT 'pending' -- 'pending', 'approved', 'rejected'
);