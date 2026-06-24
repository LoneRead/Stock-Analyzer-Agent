#!/usr/bin/env python3
"""Stock Market AI Agent — CLI entry point."""

from __future__ import annotations

import argparse
import sys

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from agent import StockAnalysisAgent
from config import DISCLAIMER

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Local stock market analysis and recommendations"
    )
    parser.add_argument(
        "ticker",
        help="Stock ticker symbol (e.g. AAPL, MSFT, TSLA)",
    )
    parser.add_argument(
        "--period",
        default="6mo",
        choices=["1mo", "3mo", "6mo", "1y", "2y"],
        help="Historical data period (default: 6mo)",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Ollama model to use (default: llama3.2:3b)",
    )
    parser.add_argument(
        "--rules-only",
        action="store_true",
        help="Use rule-based analysis instead of Ollama",
    )
    args = parser.parse_args()

    try:
        status = f"[bold green]Analyzing {args.ticker.upper()}"
        if not args.rules_only:
            model = args.model or "llama3.2:3b"
            status += f" with {model}"
        status += "..."
        with console.status(status):
            agent = StockAnalysisAgent(model=args.model, use_ollama=not args.rules_only)
            result = agent.analyze(args.ticker, period=args.period)
    except ValueError as e:
        console.print(f"[bold red]Error:[/] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]Analysis failed:[/] {e}")
        sys.exit(1)

    _render_report(result)


def _render_report(result: dict) -> None:
    ticker = result["ticker"]
    name = result["company_name"]
    analysis = result["analysis"]
    market = result["market_data"]
    price = market["price_action"]
    fundamentals = market["fundamentals"]
    technicals = market["technical_indicators"]

    currency_symbol = fundamentals.get("currency_symbol", "$")
    rec = analysis.get("recommendation", "N/A").upper()
    confidence = analysis.get("confidence", "N/A")
    rec_color = {"BUY": "green", "HOLD": "yellow", "SELL": "red"}.get(rec, "white")

    console.print()
    console.print(
        Panel(
            f"[bold]{name}[/] ({ticker})\n"
            f"Current Price: [bold]{currency_symbol}{price['current_price']}[/]  "
            f"Day: [{'green' if price['day_change_pct'] >= 0 else 'red'}]"
            f"{price['day_change_pct']:+.2f}%[/]  "
            f"Month: [{'green' if price['month_change_pct'] >= 0 else 'red'}]"
            f"{price['month_change_pct']:+.2f}%[/]",
            title="Stock Overview",
            border_style="blue",
        )
    )

    rec_panel = Panel(
        f"[bold {rec_color}]{rec}[/]  |  Confidence: [bold]{confidence}[/]\n\n"
        f"{analysis.get('reasoning', '')}",
        title="Recommendation",
        border_style=rec_color,
    )
    console.print(rec_panel)

    console.print(Panel(analysis.get("summary", ""), title="Summary", border_style="cyan"))

    metrics = Table(title="Key Metrics", box=box.SIMPLE)
    metrics.add_column("Metric", style="dim")
    metrics.add_column("Value")
    metrics.add_row("Sector", str(fundamentals["sector"]))
    metrics.add_row("Market Cap", str(fundamentals["market_cap"]))
    metrics.add_row("P/E Ratio", str(fundamentals["pe_ratio"]))
    high_val = fundamentals.get("fifty_two_week_high", "N/A")
    low_val = fundamentals.get("fifty_two_week_low", "N/A")
    high_str = f"{currency_symbol}{high_val}" if high_val != "N/A" else "N/A"
    low_str = f"{currency_symbol}{low_val}" if low_val != "N/A" else "N/A"
    metrics.add_row("52W High / Low", f"{high_str} / {low_str}")
    metrics.add_row("RSI (14)", str(technicals["rsi_14"]))
    metrics.add_row("Trend", str(technicals["trend"]))
    metrics.add_row("SMA 20 / 50", f"{technicals['sma_20']} / {technicals['sma_50']}")
    metrics.add_row("MACD Signal", str(technicals["macd_signal_interpretation"]))
    console.print(metrics)

    console.print(Panel(analysis.get("technical_analysis", ""), title="Technical Analysis"))
    console.print(Panel(analysis.get("fundamental_analysis", ""), title="Fundamental Analysis"))

    if analysis.get("news_sentiment"):
        console.print(Panel(analysis["news_sentiment"], title="News Sentiment"))

    _render_bullet_panel("Bullish Factors", analysis.get("bullish_factors", []), "green")
    _render_bullet_panel("Bearish Factors", analysis.get("bearish_factors", []), "red")
    _render_bullet_panel("Key Risks", analysis.get("risks", []), "yellow")

    if analysis.get("price_outlook"):
        console.print(Panel(analysis["price_outlook"], title="Short-Term Outlook"))

    engine = result.get("engine", "unknown")
    model = result.get("model")
    engine_label = f"{engine} ({model})" if model and engine == "ollama" else engine
    console.print()
    console.print(f"[dim]Analysis engine: {engine_label}[/]")
    console.print(f"[dim italic]{result['disclaimer']}[/]")


def _render_bullet_panel(title: str, items: list[str], color: str) -> None:
    if not items:
        return
    text = "\n".join(f"• {item}" for item in items)
    console.print(Panel(text, title=title, border_style=color))


if __name__ == "__main__":
    main()
