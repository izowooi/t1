from __future__ import annotations
from datetime import date, timedelta
from typing import Iterable
from .config import Config
from .db import SupaDB
from .yf_client import fetch_daily_ohlc, FetchRange

def _daterange_missing(last: date | None) -> tuple[date, date | None]:
    today = date.today()
    if last is None:
        return (today - timedelta(days=400), today)
    return (last + timedelta(days=1), today)

def ingest_missing(conf: Config, only: Iterable[str] | None = None) -> None:
    key = conf.supabase_service_role_key or conf.supabase_anon_key
    if not conf.supabase_url or not key:
        raise RuntimeError("Supabase URL/Key 설정이 필요합니다 (.env).")

    db = SupaDB(conf.supabase_url, key)
    tickers = tuple(only) if only else conf.tickers
    db.ensure_tickers(tickers)

    for sym in tickers:
        last = db.get_last_date(sym)
        start, end = _daterange_missing(last)
        rows = fetch_daily_ohlc(sym, FetchRange(start=start, end=end))
        if rows:
            db.upsert_ohlc(rows)
            print(f"[ingest] {sym}: upsert {len(rows)} rows ({start}~{end})")
        else:
            print(f"[ingest] {sym}: no new rows")
