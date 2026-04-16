"""FastAPI application with endpoints."""

from fastapi import FastAPI

app = FastAPI(
    title="DevSecOps Agentic Demo",
    version="0.1.0",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}
