
MarketDataProvider Contract

Methods
--------
get_symbols() -> list[str]

get_history(
    symbol: str,
    start: date,
    end: date,
) -> pd.DataFrame

Required DataFrame columns:
- Date
- Open
- High
- Low
- Close
- Volume