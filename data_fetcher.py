from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import pandas as pd
import yfinance as yf


def fetch_stock_data(ticker: str, period: str = "6mo") -> dict[str, Any]:
    """Fetch price history, quote info, and recent news for a ticker."""
    stock = yf.Ticker(ticker.upper())
    history = stock.history(period=period)

    if history.empty:
        raise ValueError(f"No data found for ticker '{ticker}'. Check the symbol and try again.")

    info = stock.info or {}
    news = _fetch_news(stock)

    return {
        "ticker": ticker.upper(),
        "history": history,
        "info": info,
        "news": news,
        "fetched_at": datetime.now().isoformat(),
    }


def _fetch_news(stock: yf.Ticker, limit: int = 5) -> list[dict[str, str]]:
    try:
        raw_news = stock.news or []
    except Exception:
        return []

    articles = []
    for item in raw_news[:limit]:
        content = item.get("content", item)
        title = content.get("title", "")
        if not title:
            continue
        articles.append(
            {
                "title": title,
                "publisher": content.get("provider", {}).get("displayName", "Unknown"),
                "published": content.get("pubDate", content.get("providerPublishTime", "")),
            }
        )
    return articles


def summarize_price_action(history: pd.DataFrame) -> dict[str, Any]:
    """Compute key price metrics from OHLCV history."""
    close = history["Close"]
    volume = history["Volume"]

    latest = close.iloc[-1]
    prev_close = close.iloc[-2] if len(close) > 1 else latest
    day_change_pct = ((latest - prev_close) / prev_close) * 100 if prev_close else 0

    week_ago = close.iloc[-6] if len(close) >= 6 else close.iloc[0]
    month_ago = close.iloc[-22] if len(close) >= 22 else close.iloc[0]
    period_start = close.iloc[0]

    high_52w = close.max()
    low_52w = close.min()
    avg_volume_20d = volume.tail(20).mean()
    latest_volume = volume.iloc[-1]

    return {
        "current_price": round(float(latest), 2),
        "previous_close": round(float(prev_close), 2),
        "day_change_pct": round(float(day_change_pct), 2),
        "week_change_pct": round(float((latest - week_ago) / week_ago * 100), 2),
        "month_change_pct": round(float((latest - month_ago) / month_ago * 100), 2),
        "period_change_pct": round(float((latest - period_start) / period_start * 100), 2),
        "high_52w": round(float(high_52w), 2),
        "low_52w": round(float(low_52w), 2),
        "avg_volume_20d": int(avg_volume_20d),
        "latest_volume": int(latest_volume),
        "volume_vs_avg_pct": round(float((latest_volume / avg_volume_20d - 1) * 100), 2)
        if avg_volume_20d
        else 0,
    }


def summarize_fundamentals(info: dict[str, Any]) -> dict[str, Any]:
    """Extract useful fundamental data from yfinance info dict."""
    return {
        "name": info.get("longName") or info.get("shortName", "Unknown"),
        "sector": info.get("sector", "N/A"),
        "industry": info.get("industry", "N/A"),
        "market_cap": _format_large_number(info.get("marketCap")),
        "pe_ratio": _safe_round(info.get("trailingPE")),
        "forward_pe": _safe_round(info.get("forwardPE")),
        "eps": _safe_round(info.get("trailingEps")),
        "dividend_yield": _safe_round(info.get("dividendYield"), decimals=4),
        "beta": _safe_round(info.get("beta")),
        "fifty_two_week_high": _safe_round(info.get("fiftyTwoWeekHigh")),
        "fifty_two_week_low": _safe_round(info.get("fiftyTwoWeekLow")),
        "revenue_growth": _safe_round(info.get("revenueGrowth")),
        "profit_margins": _safe_round(info.get("profitMargins")),
        "analyst_target": _safe_round(info.get("targetMeanPrice")),
        "recommendation": info.get("recommendationKey", "N/A"),
    }


def _format_large_number(value: Any) -> str:
    if value is None:
        return "N/A"
    value = float(value)
    if value >= 1e12:
        return f"${value / 1e12:.2f}T"
    if value >= 1e9:
        return f"${value / 1e9:.2f}B"
    if value >= 1e6:
        return f"${value / 1e6:.2f}M"
    return f"${value:,.0f}"


def _safe_round(value: Any, decimals: int = 2) -> float | str:
    if value is None:
        return "N/A"
    return round(float(value), decimals)
