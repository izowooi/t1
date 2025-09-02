from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Optional, Tuple
import pandas as pd
from .db import OHLC

@dataclass(frozen=True)
class CrossResult:
    signal_type: str  # 'golden_cross' or 'dead_cross'
    price: float
    sma5: float
    sma60: float

def compute_sma_cross(ohlc: Iterable[OHLC]) -> Optional[Tuple[pd.DataFrame, Optional[CrossResult]]]:
    """
    Input must be in ascending date order.
    Roughly last ~65 rows are sufficient (60SMA + prev/current comparison).
    """
    rows = list(ohlc)
    if len(rows) < 61:  # need at least 60 for SMA60 plus a previous day
        return None

    df = pd.DataFrame({
        "d": [r.d for r in rows],
        "close": [r.close for r in rows],
    })
    df.set_index("d", inplace=True)

    df["sma5"] = df["close"].rolling(window=5, min_periods=5).mean()
    df["sma60"] = df["close"].rolling(window=60, min_periods=60).mean()

    valid = df.dropna().tail(2)
    if len(valid) < 2:
        return df, None

    prev, curr = valid.iloc[-2], valid.iloc[-1]
    diff_prev = float(prev["sma5"] - prev["sma60"])
    diff_curr = float(curr["sma5"] - curr["sma60"])

    cross: Optional[CrossResult] = None
    if diff_prev <= 0.0 and diff_curr > 0.0:
        cross = CrossResult("golden_cross", price=float(curr["close"]),
                            sma5=float(curr["sma5"]), sma60=float(curr["sma60"]))
    elif diff_prev >= 0.0 and diff_curr < 0.0:
        cross = CrossResult("dead_cross", price=float(curr["close"]),
                            sma5=float(curr["sma5"]), sma60=float(curr["sma60"]))
    return df, cross
