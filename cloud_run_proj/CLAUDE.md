# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

StockBot is a Python application that detects moving average crossovers (5-day vs 60-day) for NASDAQ stocks and sends notifications via Telegram and email. The system uses Supabase as the database backend and Yahoo Finance for stock data.

## Architecture

The codebase follows a modular architecture with clear separation of concerns:

- `main.py` - CLI interface with two main commands: `ingest` (data collection) and `signals` (cross detection)
- `stockbot/` - Main application module containing:
  - `config.py` - Environment configuration management
  - `db.py` - Supabase database operations
  - `yf_client.py` - Yahoo Finance API client
  - `ingest.py` - Stock data ingestion logic
  - `indicators.py` - Moving average calculations and cross detection
  - `signals.py` - Signal detection orchestration and notification dispatch
  - `notifiers.py` - Telegram and email notification handlers
- `tests/` - Unit tests using pytest
- `scripts/` - Utility scripts including Supabase connection testing

## Development Commands

### Installation
```bash
# Using pip
pip install -r requirements.txt

# Using uv (preferred)
uv sync
```

### Testing
```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=stockbot

# Run specific test markers
pytest -m "not slow"
pytest -m integration
pytest -m unit
```

### Application Commands
```bash
# Ingest stock data
python main.py ingest --tickers AAPL,GOOGL,MSFT

# Run signal detection (dry-run for testing)
python main.py signals --dry-run

# Run signal detection with debug mode (forces cross signals)
python main.py signals --debug

# Run signal detection for specific tickers
python main.py signals --tickers AAPL,GOOGL
```

### Database Testing
```bash
# Test Supabase connection
python scripts/supabase_smoke_test.py

# Apply database schema
python scripts/supabase_smoke_test.py --apply-schema

# Test with anonymous key
python scripts/supabase_smoke_test.py --use-anon

# Cleanup test data
python scripts/supabase_smoke_test.py --cleanup
```

## Key Configuration

Environment variables are managed in `config.py` and should be set in `.env`:

### Required
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_SERVICE_ROLE_KEY` or `SUPABASE_ANON_KEY` - Database access keys

### Optional
- `TICKERS` - Default comma-separated list of stock symbols
- `TELEGRAM_BOT_TOKEN` & `TELEGRAM_CHAT_ID` - For Telegram notifications  
- SMTP settings (`SMTP_HOST`, `SMTP_PORT`, etc.) - For email notifications

## Data Flow

1. **Ingestion**: `main.py ingest` → `yf_client.py` → Yahoo Finance API → `db.py` → Supabase
2. **Signal Detection**: `main.py signals` → `db.py` (fetch data) → `indicators.py` (calculate crosses) → `notifiers.py` (send alerts)

The system requires at least 60 days of historical data to calculate moving averages and detect crossovers.

## Testing Strategy

- Unit tests focus on the `indicators.py` module with comprehensive cross-detection scenarios
- Integration testing available for database operations
- Test markers: `unit`, `integration`, `slow`
- Fixtures provide sample OHLC data for reproducible tests

## Development Notes

- Uses Python 3.12+ with type hints throughout
- Dataclasses for configuration and data models
- Async/await patterns not used - synchronous operations only
- Error handling focuses on graceful degradation (missing notifications don't crash ingestion)
- Debug mode available for testing signal detection without waiting for actual crosses