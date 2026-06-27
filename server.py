import os
import sys
import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from agent import StockAnalysisAgent

app = FastAPI(
    title="Stock Market AI Agent API",
    description="Backend API for local stock analysis and recommendations",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/analyze")
async def analyze_ticker(
    ticker: str = Query(..., description="Stock ticker symbol (e.g. AAPL, MSFT)"),
    period: str = Query("6mo", description="Historical data period"),
    rules_only: bool = Query(False, description="Use rule-based analysis instead of Ollama AI"),
    model: str = Query(None, description="Ollama model to use")
):
    if not ticker or not ticker.strip():
        raise HTTPException(status_code=400, detail="Ticker symbol cannot be empty.")
    
    try:
        agent = StockAnalysisAgent(model=model, use_ollama=not rules_only)
        result = agent.analyze(ticker.strip(), period=period)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# Ensure static directory exists
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
    os.makedirs(os.path.join(static_dir, "css"))
    os.makedirs(os.path.join(static_dir, "js"))

# Serve index.html at root explicitly to ensure it works
@app.get("/")
async def read_index():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Welcome to Stock Analyzer Agent API. Frontend files not found yet."}

# Mount the static directory for other static files like CSS and JS
app.mount("/static", StaticFiles(directory=static_dir), name="static")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"Starting server on http://localhost:{port}")
    uvicorn.run("server:app", host="127.0.0.1", port=port, reload=True)
