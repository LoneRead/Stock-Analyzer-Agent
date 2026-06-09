from __future__ import annotations

from typing import Any

from config import DISCLAIMER, OLLAMA_MODEL
from data_fetcher import (
    fetch_stock_data,
    summarize_fundamentals,
    summarize_price_action,
)
from indicators import compute_indicators
from local_analyzer import analyze_stock as analyze_with_rules
from ollama_analyzer import analyze_stock as analyze_with_ollama


class StockAnalysisAgent:
    def __init__(self, model: str | None = None, use_ollama: bool = True):
        self.model = model or OLLAMA_MODEL
        self.use_ollama = use_ollama

    def analyze(self, ticker: str, period: str = "6mo") -> dict[str, Any]:
        """Run full analysis pipeline for a stock ticker."""
        raw_data = fetch_stock_data(ticker, period=period)
        price_summary = summarize_price_action(raw_data["history"])
        fundamentals = summarize_fundamentals(raw_data["info"])
        technicals = compute_indicators(raw_data["history"])

        context = {
            "ticker": raw_data["ticker"],
            "price_action": price_summary,
            "fundamentals": fundamentals,
            "technical_indicators": technicals,
            "recent_news": raw_data["news"],
            "data_period": period,
        }

        engine = "rules"
        if self.use_ollama:
            try:
                analysis = analyze_with_ollama(context, model=self.model)
                engine = "ollama"
            except Exception as exc:
                analysis = analyze_with_rules(context)
                engine = f"rules (Ollama unavailable: {exc})"
        else:
            analysis = analyze_with_rules(context)

        return {
            "ticker": raw_data["ticker"],
            "company_name": fundamentals["name"],
            "fetched_at": raw_data["fetched_at"],
            "market_data": context,
            "analysis": analysis,
            "engine": engine,
            "model": self.model if self.use_ollama else None,
            "disclaimer": DISCLAIMER,
        }
