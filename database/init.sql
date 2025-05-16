-- 创建数据库表结构

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 旅行计划表
CREATE TABLE IF NOT EXISTS trip_plans (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    origin VARCHAR(100) NOT NULL,
    destination VARCHAR(100) NOT NULL,
    preferences TEXT[] NOT NULL,
    duration INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 路线信息表
CREATE TABLE IF NOT EXISTS routes (
    id SERIAL PRIMARY KEY,
    trip_plan_id INTEGER REFERENCES trip_plans(id),
    origin VARCHAR(100) NOT NULL,
    destination VARCHAR(100) NOT NULL,
    distance VARCHAR(50),
    duration VARCHAR(50),
    steps TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 天气信息表
CREATE TABLE IF NOT EXISTS weather_forecasts (
    id SERIAL PRIMARY KEY,
    trip_plan_id INTEGER REFERENCES trip_plans(id),
    location VARCHAR(100) NOT NULL,
    date DATE NOT NULL,
    temperature_min FLOAT,
    temperature_max FLOAT,
    condition VARCHAR(50),
    humidity INTEGER,
    wind_speed FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 景点信息表
CREATE TABLE IF NOT EXISTS pois (
    id SERIAL PRIMARY KEY,
    trip_plan_id INTEGER REFERENCES trip_plans(id),
    name VARCHAR(200) NOT NULL,
    category VARCHAR(50),
    rating FLOAT,
    address TEXT,
    latitude FLOAT,
    longitude FLOAT,
    description TEXT,
    price_level INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI总结表
CREATE TABLE IF NOT EXISTS ai_summaries (
    id SERIAL PRIMARY KEY,
    trip_plan_id INTEGER REFERENCES trip_plans(id),
    summary TEXT NOT NULL,
    recommendations TEXT,
    tips TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_trip_plans_user_id ON trip_plans(user_id);
CREATE INDEX IF NOT EXISTS idx_routes_trip_plan_id ON routes(trip_plan_id);
CREATE INDEX IF NOT EXISTS idx_weather_trip_plan_id ON weather_forecasts(trip_plan_id);
CREATE INDEX IF NOT EXISTS idx_pois_trip_plan_id ON pois(trip_plan_id);
CREATE INDEX IF NOT EXISTS idx_ai_summaries_trip_plan_id ON ai_summaries(trip_plan_id);

-- 插入示例数据
INSERT INTO users (username, email) VALUES 
('demo_user', 'demo@example.com')
ON CONFLICT (username) DO NOTHING;
