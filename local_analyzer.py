from __future__ import annotations

from typing import Any


def analyze_stock(context: dict[str, Any]) -> dict[str, Any]:
    """Produce structured stock analysis from market data using local rules."""
    price = context["price_action"]
    fundamentals = context["fundamentals"]
    technicals = context["technical_indicators"]
    news = context.get("recent_news", [])
    ticker = context["ticker"]
    period = context.get("data_period", "6mo")

    bullish, bearish = _collect_signals(price, fundamentals, technicals)
    risks = _collect_risks(price, fundamentals, technicals)
    recommendation, confidence, score = _score_recommendation(bullish, bearish)

    return {
        "summary": _build_summary(ticker, fundamentals["name"], price, recommendation, confidence),
        "technical_analysis": _build_technical_analysis(price, technicals, period),
        "fundamental_analysis": _build_fundamental_analysis(fundamentals),
        "news_sentiment": _build_news_sentiment(news),
        "bullish_factors": bullish or ["No strong bullish signals in current data"],
        "bearish_factors": bearish or ["No strong bearish signals in current data"],
        "risks": risks,
        "recommendation": recommendation,
        "confidence": confidence,
        "reasoning": _build_reasoning(recommendation, score, technicals, fundamentals),
        "price_outlook": _build_price_outlook(price, technicals, recommendation),
    }


def _collect_signals(
    price: dict[str, Any],
    fundamentals: dict[str, Any],
    technicals: dict[str, Any],
) -> tuple[list[str], list[str]]:
    bullish: list[str] = []
    bearish: list[str] = []

    if price["day_change_pct"] > 0:
        bullish.append(f"Price up {price['day_change_pct']:+.2f}% today")
    elif price["day_change_pct"] < 0:
        bearish.append(f"Price down {price['day_change_pct']:+.2f}% today")

    if price["month_change_pct"] > 5:
        bullish.append(f"Strong monthly gain of {price['month_change_pct']:+.2f}%")
    elif price["month_change_pct"] < -5:
        bearish.append(f"Monthly decline of {price['month_change_pct']:+.2f}%")

    if price["period_change_pct"] > 10:
        bullish.append(f"Up {price['period_change_pct']:+.2f}% over the analysis period")
    elif price["period_change_pct"] < -10:
        bearish.append(f"Down {price['period_change_pct']:+.2f}% over the analysis period")

    trend = str(technicals["trend"])
    if "Bullish" in trend:
        bullish.append(f"Trend is {trend.lower()}")
    elif "Bearish" in trend:
        bearish.append(f"Trend is {trend.lower()}")

    rsi_signal = str(technicals["rsi_signal"])
    rsi = technicals["rsi_14"]
    if rsi_signal == "Oversold":
        bullish.append(f"RSI at {rsi} suggests oversold conditions (potential bounce)")
    elif rsi_signal == "Overbought":
        bearish.append(f"RSI at {rsi} suggests overbought conditions (potential pullback)")

    macd_interp = str(technicals["macd_signal_interpretation"])
    if "Bullish" in macd_interp:
        bullish.append(f"MACD shows {macd_interp.lower()}")
    elif "Bearish" in macd_interp:
        bearish.append(f"MACD shows {macd_interp.lower()}")

    price_vs_sma20 = technicals["price_vs_sma20_pct"]
    if isinstance(price_vs_sma20, (int, float)):
        if price_vs_sma20 > 2:
            bullish.append(f"Trading {price_vs_sma20:+.2f}% above 20-day SMA")
        elif price_vs_sma20 < -2:
            bearish.append(f"Trading {price_vs_sma20:+.2f}% below 20-day SMA")

    volume_pct = price.get("volume_vs_avg_pct", 0)
    if isinstance(volume_pct, (int, float)) and volume_pct > 50:
        direction = "bullish" if price["day_change_pct"] >= 0 else "bearish"
        signal = bullish if direction == "bullish" else bearish
        signal.append(f"Volume {volume_pct:+.0f}% above 20-day average ({direction} confirmation)")

    revenue_growth = fundamentals.get("revenue_growth")
    if isinstance(revenue_growth, (int, float)) and revenue_growth > 0.1:
        bullish.append(f"Revenue growing at {revenue_growth * 100:.1f}%")
    elif isinstance(revenue_growth, (int, float)) and revenue_growth < 0:
        bearish.append(f"Revenue declining ({revenue_growth * 100:.1f}%)")

    profit_margins = fundamentals.get("profit_margins")
    if isinstance(profit_margins, (int, float)) and profit_margins > 0.15:
        bullish.append(f"Healthy profit margins at {profit_margins * 100:.1f}%")

    analyst_rec = str(fundamentals.get("recommendation", "N/A")).lower()
    if analyst_rec in ("buy", "strong_buy"):
        bullish.append(f"Analyst consensus: {analyst_rec.replace('_', ' ')}")
    elif analyst_rec in ("sell", "strong_sell"):
        bearish.append(f"Analyst consensus: {analyst_rec.replace('_', ' ')}")

    current = price["current_price"]
    high_52w = fundamentals.get("fifty_two_week_high")
    low_52w = fundamentals.get("fifty_two_week_low")
    if isinstance(high_52w, (int, float)) and isinstance(low_52w, (int, float)):
        range_position = (current - low_52w) / (high_52w - low_52w) if high_52w != low_52w else 0.5
        if range_position > 0.85:
            bearish.append(f"Near 52-week high (${high_52w:.2f}) — limited upside room")
        elif range_position < 0.15:
            bullish.append(f"Near 52-week low (${low_52w:.2f}) — potential value entry")

    return bullish, bearish


def _collect_risks(
    price: dict[str, Any],
    fundamentals: dict[str, Any],
    technicals: dict[str, Any],
) -> list[str]:
    risks: list[str] = []

    beta = fundamentals.get("beta")
    if isinstance(beta, (int, float)) and beta > 1.3:
        risks.append(f"High beta ({beta:.2f}) — more volatile than the broader market")

    pe = fundamentals.get("pe_ratio")
    if isinstance(pe, (int, float)) and pe > 40:
        risks.append(f"Elevated P/E ratio ({pe:.1f}) — valuation may be stretched")

    if str(technicals["rsi_signal"]) == "Overbought":
        risks.append("RSI in overbought territory — short-term correction risk")

    if price["month_change_pct"] < -10:
        risks.append("Significant recent price weakness may indicate deteriorating sentiment")

    if str(technicals["trend"]) == "Mixed / consolidating":
        risks.append("Mixed trend signals — direction unclear, wait for confirmation")

    risks.append("Past performance does not guarantee future results")
    risks.append("Macro events and sector-wide moves can override individual stock signals")

    return risks


def _score_recommendation(
    bullish: list[str], bearish: list[str]
) -> tuple[str, str, int]:
    score = len(bullish) - len(bearish)

    if score >= 3:
        recommendation = "BUY"
    elif score <= -3:
        recommendation = "SELL"
    else:
        recommendation = "HOLD"

    gap = abs(score)
    if gap >= 5:
        confidence = "High"
    elif gap >= 2:
        confidence = "Medium"
    else:
        confidence = "Low"

    return recommendation, confidence, score


def _build_summary(
    ticker: str, name: str, price: dict[str, Any], recommendation: str, confidence: str
) -> str:
    direction = "higher" if price["day_change_pct"] >= 0 else "lower"
    return (
        f"{name} ({ticker}) is trading at ${price['current_price']}, "
        f"{abs(price['day_change_pct']):.2f}% {direction} on the day. "
        f"Based on technical indicators, fundamentals, and price action, "
        f"the local analysis engine suggests {recommendation} with {confidence.lower()} confidence."
    )


def _build_technical_analysis(
    price: dict[str, Any], technicals: dict[str, Any], period: str
) -> str:
    return (
        f"Over the past {period}, the stock has moved {price['period_change_pct']:+.2f}%. "
        f"The current trend is classified as \"{technicals['trend']}\". "
        f"RSI (14) reads {technicals['rsi_14']} ({technicals['rsi_signal']}), "
        f"with SMA 20/50 at {technicals['sma_20']} / {technicals['sma_50']}. "
        f"The stock is {technicals['price_vs_sma20_pct']}% vs the 20-day SMA. "
        f"MACD interpretation: {technicals['macd_signal_interpretation']}."
    )


def _build_fundamental_analysis(fundamentals: dict[str, Any]) -> str:
    return (
        f"{fundamentals['name']} operates in the {fundamentals['sector']} sector "
        f"({fundamentals['industry']}). Market cap is {fundamentals['market_cap']} "
        f"with a trailing P/E of {fundamentals['pe_ratio']} and forward P/E of {fundamentals['forward_pe']}. "
        f"EPS is {fundamentals['eps']}, beta is {fundamentals['beta']}, "
        f"and analyst consensus is \"{fundamentals['recommendation']}\" "
        f"with a mean price target of {fundamentals['analyst_target']}."
    )


def _build_news_sentiment(news: list[dict[str, str]]) -> str:
    if not news:
        return "No recent news headlines were available for sentiment analysis."

    headlines = "; ".join(item["title"] for item in news[:3])
    return (
        f"Recent headlines include: {headlines}. "
        "Review these stories directly for sentiment — automated local analysis "
        "does not perform deep news NLP."
    )


def _build_reasoning(
    recommendation: str,
    score: int,
    technicals: dict[str, Any],
    fundamentals: dict[str, Any],
) -> str:
    if recommendation == "BUY":
        return (
            f"Bullish signals outweigh bearish ones (net score: {score:+d}). "
            f"Trend is \"{technicals['trend']}\" with RSI at {technicals['rsi_14']}."
        )
    if recommendation == "SELL":
        return (
            f"Bearish signals outweigh bullish ones (net score: {score:+d}). "
            f"Trend is \"{technicals['trend']}\" with RSI at {technicals['rsi_14']}."
        )
    return (
        f"Signals are mixed (net score: {score:+d}), suggesting a wait-and-see approach. "
        f"Analyst consensus is \"{fundamentals['recommendation']}\"."
    )


def _build_price_outlook(
    price: dict[str, Any], technicals: dict[str, Any], recommendation: str
) -> str:
    rsi_signal = str(technicals["rsi_signal"])
    if recommendation == "BUY":
        outlook = "Potential for continued upward momentum"
    elif recommendation == "SELL":
        outlook = "Risk of further downside pressure"
    else:
        outlook = "Likely range-bound trading near current levels"

    if rsi_signal == "Overbought":
        outlook += ", though overbought RSI may cap near-term gains"
    elif rsi_signal == "Oversold":
        outlook += ", with oversold RSI suggesting a possible relief rally"

    outlook += (
        f". Key levels to watch: SMA 20 at {technicals['sma_20']} "
        f"and SMA 50 at {technicals['sma_50']}."
    )
    return outlook
