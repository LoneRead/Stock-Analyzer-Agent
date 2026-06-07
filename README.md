# Stock Market AI Agent

An AI-powered agent that fetches live market data, runs technical analysis, and produces investment summaries with BUY / HOLD / SELL recommendations.

## Features

- **Live market data** via Yahoo Finance (prices, volume, fundamentals, news)
- **Technical indicators** — SMA (20/50/200), RSI, MACD
- **AI analysis** — structured summary, bullish/bearish factors, risks, and recommendations
- **CLI interface** — rich terminal output with color-coded recommendations

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API key

Copy the example env file and add your OpenAI API key:

```bash
copy .env.example .env
```

Edit `.env`:

```
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
```

### 3. Run an analysis

```bash
python main.py AAPL
python main.py MSFT --period 1y
python main.py TSLA --period 3mo
```

## Example Output

The agent prints:

- Stock overview (price, daily/monthly change)
- **Recommendation** (BUY / HOLD / SELL) with confidence level
- Executive summary
- Key metrics table (P/E, RSI, trend, etc.)
- Technical and fundamental analysis
- Bullish / bearish factors and risks
- Short-term price outlook

## Project Structure

```
├── main.py           # CLI entry point
├── agent.py          # AI agent (orchestrates data + LLM)
├── data_fetcher.py   # Yahoo Finance data fetching
├── indicators.py     # Technical indicator calculations
├── config.py         # Environment configuration
├── requirements.txt
└── .env.example
```

## How It Works

```
Ticker Input
    ↓
Fetch Data (yfinance) ──→ Price history, fundamentals, news
    ↓
Compute Indicators ──→ RSI, MACD, SMA, trend
    ↓
Build Context ──→ Structured JSON for the LLM
    ↓
AI Analysis (OpenAI) ──→ Summary + Recommendation
    ↓
Display Report (CLI)
```

## Disclaimer

This tool generates AI analysis for **informational purposes only**. It is **not financial advice**. Always do your own research and consult a licensed financial advisor before making investment decisions.

## Roadmap

- [ ] Multi-stock portfolio analysis
- [ ] Web dashboard (FastAPI + React)
- [ ] Scheduled daily reports
- [ ] Additional data sources (Alpha Vantage, news sentiment APIs)
- [ ] Backtesting recommendations
=======
# Stock-Analyzer-Agent
>>>>>>> 67d2f95ac317f54bc534ae53887934fb74f2b054
