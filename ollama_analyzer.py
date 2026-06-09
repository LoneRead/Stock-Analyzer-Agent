from __future__ import annotations

import json
import re
from typing import Any

from ollama import Client

from config import OLLAMA_HOST, OLLAMA_MODEL

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

REQUIRED_FIELDS = (
    "summary",
    "technical_analysis",
    "fundamental_analysis",
    "news_sentiment",
    "bullish_factors",
    "bearish_factors",
    "risks",
    "recommendation",
    "confidence",
    "reasoning",
    "price_outlook",
)


def analyze_stock(
    context: dict[str, Any],
    model: str | None = None,
    host: str | None = None,
) -> dict[str, Any]:
    """Run analysis through a local Ollama model."""
    client = Client(host=host or OLLAMA_HOST)
    user_prompt = (
        f"Analyze this stock and provide your recommendation.\n\n"
        f"DATA:\n{json.dumps(context, indent=2, default=str)}"
    )

    response = client.chat(
        model=model or OLLAMA_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        format="json",
        options={"temperature": 0.3},
    )

    content = response["message"]["content"]
    return _parse_analysis(content)


def _parse_analysis(content: str) -> dict[str, Any]:
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if not match:
            raise ValueError("Ollama returned a response that could not be parsed as JSON.")
        data = json.loads(match.group())

    missing = [field for field in REQUIRED_FIELDS if field not in data]
    if missing:
        raise ValueError(f"Ollama response missing fields: {', '.join(missing)}")

    data["recommendation"] = str(data["recommendation"]).upper().split()[0]
    if data["recommendation"] not in {"BUY", "HOLD", "SELL"}:
        raise ValueError(f"Invalid recommendation: {data['recommendation']}")

    return data
