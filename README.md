# Stock Market Analyzer

A locally-run stock analysis tool that fetches live market data, computes technical indicators, and produces investment summaries with BUY / HOLD / SELL recommendations — powered by **Ollama** (no cloud API keys).

## Features

- **Live market data** via Yahoo Finance (prices, volume, fundamentals, news)
- **Technical indicators** — SMA (20/50/200), RSI, MACD
- **Local LLM analysis** via Ollama (default: `llama3.2:3b`)
- **Rule-based fallback** if Ollama is unavailable
- **CLI interface** — rich terminal output with color-coded recommendations
- **Web Dashboard UI** — interactive local web application to search tickers, select periods, toggle analysis mode (Rules vs. AI), and visualize stock metrics & charts

## Prerequisites

- [Ollama](https://ollama.com/) installed and running
- A local model pulled, e.g.:

```bash
ollama pull llama3.2:3b
# or
ollama pull qwen2.5:1.5b
```

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Web Dashboard

To launch the web interface:

```bash
python server.py
```

Then open your browser and navigate to **[http://localhost:8000](http://localhost:8000)**.

### 3. Run a CLI-based analysis

```bash
python main.py AAPL
python main.py MSFT --period 1y
python main.py TSLA --model qwen2.5:1.5b
python main.py NVDA --rules-only
```

### CLI options

| Flag | Description |
|------|-------------|
| `--period` | Historical window: `1mo`, `3mo`, `6mo`, `1y`, `2y` |
| `--model` | Ollama model name (default: `llama3.2:3b`) |
| `--rules-only` | Skip Ollama, use rule-based analysis |

Set a default model via environment variable:

```bash
set OLLAMA_MODEL=qwen2.5:1.5b
```

## Project Structure

```
├── main.py            # CLI entry point
├── server.py          # FastAPI web server & static files host
├── agent.py           # Orchestrates data fetching + analysis
├── ollama_analyzer.py # Ollama LLM analysis
├── local_analyzer.py  # Rule-based fallback engine
├── data_fetcher.py    # Yahoo Finance data fetching
├── indicators.py      # Technical indicator calculations
├── config.py          # App configuration
├── requirements.txt
└── static/            # Frontend assets (HTML, CSS, JS)
```

## How It Works

```
Ticker Input
    ↓
Fetch Data (yfinance) ──→ Price history, fundamentals, news
    ↓
Compute Indicators ──→ RSI, MACD, SMA, trend
    ↓
Build Context ──→ Structured JSON
    ↓
Ollama (local LLM) ──→ Summary + Recommendation
    ↓ (fallback if Ollama fails)
Rule-based engine
    ↓
Display Report (CLI)
```

## Disclaimer

This tool generates analysis for **informational purposes only**. It is **not financial advice**. Always do your own research and consult a licensed financial advisor before making investment decisions.
