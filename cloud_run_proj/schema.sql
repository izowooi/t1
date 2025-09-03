create table if not exists public.tickers (
  ticker text primary key,
  name   text,
  exchange text default 'NASDAQ'
);

create table if not exists public.ohlc_daily (
  ticker text references public.tickers(ticker) on delete cascade,
  d date not null,
  open  double precision,
  high  double precision,
  low   double precision,
  close double precision not null,
  volume bigint,
  primary key (ticker, d)
);

create index if not exists idx_ohlc_daily_ticker_date_desc
  on public.ohlc_daily (ticker, d desc);

create table if not exists public.signals (
  id bigserial primary key,
  ticker text not null references public.tickers(ticker) on delete cascade,
  d date not null,
  signal_type text not null check (signal_type in ('golden_cross','dead_cross')),
  price double precision not null,
  sma5 double precision not null,
  sma60 double precision not null,
  created_at timestamptz not null default now(),
  unique (ticker, d, signal_type)
);

-- Optional: RLS to allow public read-only access
alter table if exists public.ohlc_daily enable row level security;
create policy if not exists ohlc_read on public.ohlc_daily for select using (true);
alter table if exists public.tickers enable row level security;
create policy if not exists tickers_read on public.tickers for select using (true);
alter table if exists public.signals enable row level security;
create policy if not exists signals_read on public.signals for select using (true);
