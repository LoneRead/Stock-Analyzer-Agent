import os

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

DISCLAIMER = (
    "This analysis is generated locally for informational purposes only. "
    "It is not financial advice. Always do your own research and consult "
    "a licensed financial advisor before making investment decisions."
)
