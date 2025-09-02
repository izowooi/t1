from __future__ import annotations
from dataclasses import dataclass
from datetime import date, timedelta
import pandas as pd
import yfinance as yf
from .db import OHLC

@dataclass(frozen=True)
class FetchRange:
    start: date
    end: date | None  # inclusive end; None=through today

    def __post_init__(self):
        if self.end is not None and self.end < self.start:
            raise ValueError("end must be >= start")

def fetch_daily_ohlc(ticker: str, rng: FetchRange) -> list[OHLC]:
    from datetime import timedelta
    import pandas as pd
    import yfinance as yf
    from .db import OHLC

    start = rng.start.isoformat()
    end = ((rng.end + timedelta(days=1)).isoformat() if rng.end else None)

    df = yf.download(
        tickers=ticker,
        start=start,
        end=end,
        interval="1d",
        progress=False,
        auto_adjust=False,
        actions=False,
        threads=False,
    )
    if df.empty:
        return []

    # 1) 항상 reset_index → 날짜 컬럼을 확실히 확보
    df = df.reset_index()

    # 2) 날짜 컬럼 확정 후 date 로 변환
    #    (yfinance는 보통 'Date', 드물게 다른 이름일 수 있어 fallback)
    date_col = "Date" if "Date" in df.columns else df.columns[0]
    df["d"] = pd.to_datetime(df[date_col]).dt.date

    # 3) 필요한 컬럼만 선택(Adj Close 등은 무시), 순서 고정
    wanted = [c for c in ["Open", "High", "Low", "Close", "Volume", "d"] if c in df.columns]
    df = df[wanted]

    # 4) dict 레코드로 안전하게 순회 (열명이 어떤 상태여도 안전)
    rows: list[OHLC] = []
    for rec in df.to_dict("records"):
        o = float(rec[('Open', ticker)]) if ('Open', ticker) in rec and pd.notna(rec[('Open', ticker)]) else None
        h = float(rec[('High', ticker)]) if ('High', ticker) in rec and pd.notna(rec[('High', ticker)]) else None
        l = float(rec[('Low', ticker)]) if ('Low', ticker) in rec and pd.notna(rec[('Low', ticker)]) else None
        c = float(rec[('Close', ticker)]) if ('Close', ticker) in rec and pd.notna(rec[('Close', ticker)]) else None
        v = int(rec[('Volume', ticker)]) if ('Volume', ticker) in rec and pd.notna(rec[('Volume', ticker)]) else None
        # d 값은 기존 로직 유지
        d = rec.get(('d', '')) if isinstance(rec.get(('d', '')), date) else None

        rows.append(OHLC(
            ticker=ticker.upper(),
            d=d,
            open=o, high=h, low=l, close=c, volume=v,
        ))
    return rows

