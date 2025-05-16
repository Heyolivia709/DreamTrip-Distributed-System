-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY, -- user ID
    username VARCHAR(50) UNIQUE NOT NULL, -- username
    email VARCHAR(100) UNIQUE NOT NULL, -- user email
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- creation time
);

-- Trip plans table
CREATE TABLE IF NOT EXISTS trip_plans (
    id SERIAL PRIMARY KEY, -- trip plan ID
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE, -- related user
    origin VARCHAR(100) NOT NULL, -- start location
    destination VARCHAR(100) NOT NULL, -- end location
    preferences TEXT[] NOT NULL, -- user preferences
    duration INTEGER NOT NULL, -- trip duration (days)
    status VARCHAR(20) DEFAULT 'pending', -- current status
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- creation time
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- last update time
);

-- Routes table
CREATE TABLE IF NOT EXISTS routes (
    id SERIAL PRIMARY KEY, -- route ID
    trip_plan_id INTEGER REFERENCES trip_plans(id) ON DELETE CASCADE, -- related trip plan
    origin VARCHAR(100) NOT NULL, -- route start
    destination VARCHAR(100) NOT NULL, -- route end
    distance VARCHAR(50), -- distance
    duration VARCHAR(50), -- time duration
    steps TEXT[], -- route steps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- creation time
);

-- Weather forecasts table
CREATE TABLE IF NOT EXISTS weather_forecasts (
    id SERIAL PRIMARY KEY, -- forecast ID
    trip_plan_id INTEGER REFERENCES trip_plans(id) ON DELETE CASCADE, -- related trip plan
    location VARCHAR(100) NOT NULL, -- location name
    date DATE NOT NULL, -- forecast date
    temperature_min FLOAT, -- min temperature
    temperature_max FLOAT, -- max temperature
    condition VARCHAR(50), -- weather condition
    humidity INTEGER, -- humidity percentage
    wind_speed FLOAT, -- wind speed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- creation time
);

-- Points of interest (POI) table
CREATE TABLE IF NOT EXISTS pois (
    id SERIAL PRIMARY KEY, -- POI ID
    trip_plan_id INTEGER REFERENCES trip_plans(id) ON DELETE CASCADE, -- related trip plan
    name VARCHAR(200) NOT NULL, -- POI name
    category VARCHAR(50), -- POI category
    rating FLOAT, -- rating score
    address TEXT, -- address
    latitude FLOAT, -- latitude
    longitude FLOAT, -- longitude
    description TEXT, -- description
    price_level INTEGER, -- price level
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- creation time
);

-- AI summaries table
CREATE TABLE IF NOT EXISTS ai_summaries (
    id SERIAL PRIMARY KEY, -- summary ID
    trip_plan_id INTEGER REFERENCES trip_plans(id) ON DELETE CASCADE, -- related trip plan
    summary TEXT NOT NULL, -- AI summary text
    recommendations TEXT, -- recommendations
    tips TEXT, -- travel tips
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- creation time
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_trip_plans_user_id ON trip_plans(user_id);
CREATE INDEX IF NOT EXISTS idx_routes_trip_plan_id ON routes(trip_plan_id);
CREATE INDEX IF NOT EXISTS idx_weather_trip_plan_id ON weather_forecasts(trip_plan_id);
CREATE INDEX IF NOT EXISTS idx_pois_trip_plan_id ON pois(trip_plan_id);
CREATE INDEX IF NOT EXISTS idx_ai_summaries_trip_plan_id ON ai_summaries(trip_plan_id);

-- Sample data
INSERT INTO users (username, email) VALUES 
('demo_user', 'demo@example.com');