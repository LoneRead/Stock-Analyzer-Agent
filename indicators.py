from __future__ import annotations

import pandas as pd


def compute_indicators(history: pd.DataFrame) -> dict[str, float | str]:
    """Calculate common technical indicators from OHLCV data."""
    close = history["Close"]
    high = history["High"]
    low = history["Low"]

    sma_20 = close.rolling(20).mean().iloc[-1]
    sma_50 = close.rolling(50).mean().iloc[-1] if len(close) >= 50 else None
    sma_200 = close.rolling(200).mean().iloc[-1] if len(close) >= 200 else None

    rsi = _compute_rsi(close, period=14)
    macd_line, signal_line, histogram = _compute_macd(close)

    latest = close.iloc[-1]
    trend = _determine_trend(latest, sma_20, sma_50)

    return {
        "sma_20": _round_or_na(sma_20),
        "sma_50": _round_or_na(sma_50),
        "sma_200": _round_or_na(sma_200),
        "rsi_14": _round_or_na(rsi),
        "macd": _round_or_na(macd_line),
        "macd_signal": _round_or_na(signal_line),
        "macd_histogram": _round_or_na(histogram),
        "price_vs_sma20_pct": _pct_diff(latest, sma_20),
        "price_vs_sma50_pct": _pct_diff(latest, sma_50),
        "trend": trend,
        "rsi_signal": _rsi_signal(rsi),
        "macd_signal_interpretation": _macd_signal(macd_line, signal_line, histogram),
    }


def _compute_rsi(close: pd.Series, period: int = 14) -> float | None:
    if len(close) < period + 1:
        return None

    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss.replace(0, float("nan"))
    rsi = 100 - (100 / (1 + rs))
    value = rsi.iloc[-1]
    return float(value) if pd.notna(value) else None


def _compute_macd(
    close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
) -> tuple[float | None, float | None, float | None]:
    if len(close) < slow + signal:
        return None, None, None

    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line

    return (
        float(macd_line.iloc[-1]),
        float(signal_line.iloc[-1]),
        float(histogram.iloc[-1]),
    )


def _determine_trend(
    price: float, sma_20: float | None, sma_50: float | None
) -> str:
    if sma_20 is None or pd.isna(sma_20):
        return "Insufficient data"

    if sma_50 is None or pd.isna(sma_50):
        return "Bullish" if price > sma_20 else "Bearish"

    if price > sma_20 > sma_50:
        return "Bullish (price above SMA 20 & 50)"
    if price < sma_20 < sma_50:
        return "Bearish (price below SMA 20 & 50)"
    return "Mixed / consolidating"


def _rsi_signal(rsi: float | None) -> str:
    if rsi is None or pd.isna(rsi):
        return "N/A"
    if rsi >= 70:
        return "Overbought"
    if rsi <= 30:
        return "Oversold"
    return "Neutral"


def _macd_signal(
    macd: float | None, signal: float | None, histogram: float | None
) -> str:
    if any(v is None or pd.isna(v) for v in (macd, signal, histogram)):
        return "N/A"
    if histogram > 0 and macd > signal:
        return "Bullish momentum"
    if histogram < 0 and macd < signal:
        return "Bearish momentum"
    return "Neutral / crossover pending"


def _round_or_na(value: float | None, decimals: int = 2) -> float | str:
    if value is None or pd.isna(value):
        return "N/A"
    return round(float(value), decimals)


def _pct_diff(price: float, reference: float | None) -> float | str:
    if reference is None or pd.isna(reference) or reference == 0:
        return "N/A"
    return round((price - reference) / reference * 100, 2)
