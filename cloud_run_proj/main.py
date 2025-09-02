from __future__ import annotations
import argparse
from stockbot.config import Config
from stockbot.ingest import ingest_missing
from stockbot.signals import run_signal_detection

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="MA(5/60) Cross Signal Bot with Supabase")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_ing = sub.add_parser("ingest", help="Fetch & upsert missing OHLC rows")
    p_ing.add_argument("--tickers", type=str, help="Comma-separated symbols (e.g., MSFT,AMZN)")

    p_sig = sub.add_parser("signals", help="Detect cross signals & notify")
    p_sig.add_argument("--tickers", type=str, help="Comma-separated symbols")
    p_sig.add_argument("--dry-run", action="store_true", help="Do not send notifications")

    return p.parse_args()

def _split(s: str | None) -> list[str] | None:
    if not s:
        return None
    return [x.strip().upper() for x in s.split(",") if x.strip()]

def main() -> None:
    args = parse_args()
    conf = Config.from_env()

    if args.cmd == "ingest":
        ingest_missing(conf, _split(args.tickers))
    elif args.cmd == "signals":
        run_signal_detection(conf, _split(args.tickers), dry_run=args.dry_run)
    else:
        raise SystemExit(2)

if __name__ == "__main__":
    main()
