from __future__ import annotations

import json
from typing import Any

from openai import OpenAI

from config import DISCLAIMER, OPENAI_API_KEY, OPENAI_MODEL
from data_fetcher import (
    fetch_stock_data,
    summarize_fundamentals,
    summarize_price_action,
)
from indicators import compute_indicators

SYSTEM_PROMPT = """You are a professional stock market analyst AI. Your job is to analyze
provided market data and produce clear, balanced investment analysis.

Rules:
- Base your analysis ONLY on the data provided. Do not invent numbers or news.
- Be objective. Present both bullish and bearish factors.
- Clearly separate facts from interpretation.
- Your recommendation must be one of: BUY, HOLD, or SELL.
- Include a confidence level: Low, Medium, or High.
- Always acknowledge uncertainty and risks.
- Never guarantee returns or claim certainty about future prices.
- Keep language accessible to retail investors.

Respond in the following JSON format:
{
  "summary": "2-3 sentence executive summary",
  "technical_analysis": "Paragraph on price action, trends, and indicators",
  "fundamental_analysis": "Paragraph on company fundamentals and valuation",
  "news_sentiment": "Brief take on recent news if available, otherwise note lack of news",
  "bullish_factors": ["factor 1", "factor 2"],
  "bearish_factors": ["factor 1", "factor 2"],
  "risks": ["risk 1", "risk 2"],
  "recommendation": "BUY | HOLD | SELL",
  "confidence": "Low | Medium | High",
  "reasoning": "1-2 sentences explaining the recommendation",
  "price_outlook": "Short-term outlook for the next few weeks"
}"""


class StockAnalysisAgent:
    def __init__(self, api_key: str | None = None, model: str | None = None):
        key = api_key or OPENAI_API_KEY
        if not key:
            raise ValueError(
                "OpenAI API key not found. Set OPENAI_API_KEY in your .env file."
            )
        self.client = OpenAI(api_key=key)
        self.model = model or OPENAI_MODEL

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

        analysis = self._get_ai_analysis(context)

        return {
            "ticker": raw_data["ticker"],
            "company_name": fundamentals["name"],
            "fetched_at": raw_data["fetched_at"],
            "market_data": context,
            "analysis": analysis,
            "disclaimer": DISCLAIMER,
        }

    def _get_ai_analysis(self, context: dict[str, Any]) -> dict[str, Any]:
        user_prompt = (
            f"Analyze this stock and provide your recommendation.\n\n"
            f"DATA:\n{json.dumps(context, indent=2, default=str)}"
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
        )

        content = response.choices[0].message.content or "{}"
        return json.loads(content)
