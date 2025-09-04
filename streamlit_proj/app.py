# app.py
from __future__ import annotations
import os
from datetime import date, timedelta
from typing import Tuple

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from supabase import create_client, Client

# ---- Streamlit 페이지 설정
st.set_page_config(page_title="MA(5/60) Charts", layout="wide")

# ---- Supabase 클라이언트
@st.cache_resource
def get_client():
   url = st.secrets.get("supabase_url") or os.environ.get("SUPABASE_URL")
   key = st.secrets.get("supabase_anon_key") or os.environ.get("SUPABASE_ANON_KEY")
   if not url or not key:
       st.stop()  # 설정 없으면 종료
   return create_client(url, key)

sb = get_client()

# ---- 데이터 접근 함수
@st.cache_data(ttl=300)
def list_tickers() -> list[str]:
   res = sb.table("tickers").select("ticker").order("ticker").execute()
   return [r["ticker"] for r in res.data] if res.data else []

@st.cache_data(ttl=300)
def load_ohlc(ticker: str, start_d: date | None, end_d: date | None) -> pd.DataFrame:
   q = (sb.table("ohlc_daily")
          .select("d, open, high, low, close, volume")
          .eq("ticker", ticker)
          .order("d", desc=False))
   if start_d:
       q = q.gte("d", start_d.isoformat())
   if end_d:
       q = q.lte("d", end_d.isoformat())
   res = q.execute()
   df = pd.DataFrame(res.data or [])
   if df.empty:
       return df
   df["d"] = pd.to_datetime(df["d"]).dt.date
   df = df.sort_values("d").reset_index(drop=True)
   return df

def add_sma(df: pd.DataFrame) -> pd.DataFrame:
   out = df.copy()
   out["sma5"] = out["close"].rolling(5, min_periods=5).mean()
   out["sma60"] = out["close"].rolling(60, min_periods=60).mean()
   return out

def find_cross_points(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
   x = df.dropna(subset=["sma5", "sma60"]).copy()
   if x.empty:
       return x.iloc[0:0], x.iloc[0:0]  # empty dfs
   x["diff"] = x["sma5"] - x["sma60"]
   x["prev"] = x["diff"].shift(1)
   golden = x[(x["prev"] <= 0) & (x["diff"] > 0)]
   dead   = x[(x["prev"] >= 0) & (x["diff"] < 0)]
   return golden, dead

def make_chart(df: pd.DataFrame, ticker: str) -> go.Figure:
   fig = go.Figure()
   fig.add_trace(go.Scatter(x=df["d"], y=df["close"], name="Close", mode="lines"))
   if "sma5" in df:
       fig.add_trace(go.Scatter(x=df["d"], y=df["sma5"], name="SMA 5", mode="lines"))
   if "sma60" in df:
       fig.add_trace(go.Scatter(x=df["d"], y=df["sma60"], name="SMA 60", mode="lines"))

   g, d = find_cross_points(df)
   if not g.empty:
       fig.add_trace(go.Scatter(
           x=g["d"], y=g["close"], mode="markers", name="Golden Cross",
           marker=dict(symbol="triangle-up", size=10)))
   if not d.empty:
       fig.add_trace(go.Scatter(
           x=d["d"], y=d["close"], mode="markers", name="Dead Cross",
           marker=dict(symbol="triangle-down", size=10)))

   fig.update_layout(
       title=f"{ticker} — Close & SMA(5/60)",
       xaxis_title="Date",
       yaxis_title="Price",
       hovermode="x unified",
       legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
       margin=dict(l=40, r=20, t=60, b=40),
   )
   return fig

# ---- UI
st.sidebar.header("Filters")
tickers = list_tickers()
default_ticker = tickers[0] if tickers else "MSFT"
ticker = st.sidebar.selectbox("Ticker", options=tickers or ["MSFT", "AMZN", "CPNG"], index=0)

days = st.sidebar.slider("기간(일)", min_value=90, max_value=1500, value=365, step=30)
end_d = date.today()
start_d = end_d - timedelta(days=days)

st.title("Supabase → SMA(5/60) Charts")
st.caption("데이터: Supabase(ohlc_daily), 차트: Plotly — 개인 프로젝트용 대시보드")

df = load_ohlc(ticker, start_d, end_d)
if df.empty:
   st.warning("데이터가 없습니다. ingest 후 다시 시도하세요.")
   st.stop()

df = add_sma(df)
st.plotly_chart(make_chart(df, ticker), use_container_width=True)

# 표/최근 신호 등 부가 정보
st.subheader("최근 데이터")
st.dataframe(df.tail(10), use_container_width=True)
