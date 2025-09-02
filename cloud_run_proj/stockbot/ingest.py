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

    # 마지막 데이터 이후의 다음 날짜부터 오늘까지
    next_date = last + timedelta(days=1)

    # 이미 최신 데이터인 경우 (다음 날짜가 오늘보다 미래)
    if next_date > today:
        return (today, today)  # 같은 날짜로 설정하여 빈 범위 생성

    return (next_date, today)

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

        # 데이터가 이미 최신인 경우 스킵
        if end is not None and start > end:
            print(f"[ingest] {sym}: already up to date (last: {last})")
            continue

        # FetchRange 생성 시 end가 None인 경우 처리
        fetch_end = end if end is None else end
        rows = fetch_daily_ohlc(sym, FetchRange(start=start, end=fetch_end))

        if rows:
            db.upsert_ohlc(rows)
            print(f"[ingest] {sym}: upsert {len(rows)} rows ({start}~{end or 'today'})")
        else:
            print(f"[ingest] {sym}: no new rows")
