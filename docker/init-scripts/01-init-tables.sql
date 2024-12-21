-- 01-init-tables.sql
-- Purpose: Initialize TimescaleDB for storing tick and historical data

-- Create database schema
CREATE SCHEMA IF NOT EXISTS market_data;

-- Create table for historical data
CREATE TABLE IF NOT EXISTS market_data.historical_data (
    id SERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    open_time TIMESTAMP NOT NULL,
    open_price DOUBLE PRECISION NOT NULL,
    high_price DOUBLE PRECISION NOT NULL,
    low_price DOUBLE PRECISION NOT NULL,
    close_price DOUBLE PRECISION NOT NULL,
    volume DOUBLE PRECISION NOT NULL
);

-- Create table for tick data
CREATE TABLE IF NOT EXISTS market_data.tick_data (
    id SERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    tick_time TIMESTAMP NOT NULL,
    bid_price DOUBLE PRECISION NOT NULL,
    ask_price DOUBLE PRECISION NOT NULL,
    last_price DOUBLE PRECISION,
    volume DOUBLE PRECISION,
    spread DOUBLE PRECISION,
    tick_size DOUBLE PRECISION
);
