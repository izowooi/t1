# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Streamlit application that displays moving average (SMA 5/60) charts for financial data stored in Supabase. The app shows stock price charts with simple moving averages and identifies golden/dead cross signals.

## Development Commands

### Running the Application
```bash
streamlit run app.py
```

### Managing Dependencies
This project uses `uv` for dependency management:
```bash
# Install dependencies
uv install

# Add new dependency
uv add <package-name>

# Activate virtual environment
source .venv/bin/activate
```

## Architecture

### Core Components

- **app.py**: Main Streamlit application with all functionality
- **Database**: Uses Supabase as backend with two main tables:
  - `tickers`: List of available stock tickers
  - `ohlc_daily`: Daily OHLC (Open, High, Low, Close) price data
- **Configuration**: Environment variables and secrets stored in `.streamlit/secrets.toml`

### Key Functions

- `get_client()`: Creates cached Supabase client connection
- `list_tickers()`: Retrieves available stock tickers (cached for 5 minutes)
- `load_ohlc()`: Loads OHLC data for specific ticker and date range (cached for 5 minutes)
- `add_sma()`: Calculates 5-day and 60-day simple moving averages
- `find_cross_points()`: Identifies golden cross (SMA5 > SMA60) and dead cross (SMA5 < SMA60) signals
- `make_chart()`: Creates Plotly interactive chart with price lines, moving averages, and cross signals

### Data Flow

1. User selects ticker and time period via sidebar
2. App queries Supabase for OHLC data
3. Moving averages are calculated
4. Chart is generated with Plotly showing price, SMAs, and cross signals
5. Recent data is displayed in a table below the chart

## Important Notes

- The app uses Streamlit's caching (`@st.cache_data`) with 5-minute TTL for database queries
- Supabase credentials are stored in `.streamlit/secrets.toml` (not committed to git)
- The application is designed for Korean users (Korean text in UI)
- Charts use unified hover mode for better user experience
- Golden crosses are marked with upward triangles, dead crosses with downward triangles