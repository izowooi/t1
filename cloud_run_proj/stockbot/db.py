from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import Iterable, Optional, Sequence
from supabase import create_client, Client

@dataclass(frozen=True)
class OHLC:
    ticker: str
    d: date
    open: float | None
    high: float | None
    low: float | None
    close: float
    volume: int | None

class SupaDB:
    def __init__(self, url: str, key: str):
        if not url or not key:
            raise ValueError("Supabase URL/Key required")
        self.client: Client = create_client(url, key)

    # ---------- Tickers ----------
    def ensure_tickers(self, tickers: Sequence[str]) -> None:
        rows = [{"ticker": t} for t in tickers]
        self.client.table("tickers").upsert(rows, on_conflict="ticker").execute()

    # ---------- OHLC ----------
    def get_last_date(self, ticker: str) -> Optional[date]:
        res = (self.client
               .table("ohlc_daily")
               .select("d")
               .eq("ticker", ticker)
               .order("d", desc=True)
               .limit(1)
               .execute())
        data = res.data or []
        if not data:
            return None
        return date.fromisoformat(data[0]["d"][:10])

    def upsert_ohlc(self, rows: Iterable[OHLC]) -> None:
        payload = [{
            "ticker": r.ticker,
            "d": r.d.isoformat(),
            "open": r.open,
            "high": r.high,
            "low": r.low,
            "close": r.close,
            "volume": r.volume,
        } for r in rows]
        if not payload:
            return
        self.client.table("ohlc_daily").upsert(payload, on_conflict="ticker,d").execute()

    def fetch_last_n(self, ticker: str, n: int) -> list[OHLC]:
        res = (self.client
               .table("ohlc_daily")
               .select("*")
               .eq("ticker", ticker)
               .order("d", desc=True)
               .limit(n)
               .execute())
        data = res.data or []
        out: list[OHLC] = []
        for row in reversed(data):  # ascending
            out.append(OHLC(
                ticker=row["ticker"],
                d=date.fromisoformat(row["d"][:10]),
                open=row.get("open"),
                high=row.get("high"),
                low=row.get("low"),
                close=float(row["close"]),
                volume=(int(row["volume"]) if row.get("volume") is not None else None),
            ))
        return out

    # ---------- Signals ----------
    def upsert_signal(self,
                      ticker: str,
                      d: date,
                      signal_type: str,
                      price: float,
                      sma5: float,
                      sma60: float) -> None:
        payload = [{
            "ticker": ticker,
            "d": d.isoformat(),
            "signal_type": signal_type,
            "price": price,
            "sma5": sma5,
            "sma60": sma60,
        }]
        self.client.table("signals").upsert(payload, on_conflict="ticker,d,signal_type").execute()
