import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from models import Base, engine, SessionLocal
from routes import router

app = FastAPI()

# Include API router under /api prefix
app.include_router(router, prefix="/api")

# Create DB tables on startup
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

@app.get("/health", response_model=dict)
def health_check():
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
def root():
    html = """
    <html>
    <head>
        <title>QuickMark Lite</title>
        <style>
            body { background-color: #121212; color: #e0e0e0; font-family: Arial, sans-serif; padding: 2rem; }
            h1 { color: #ff9800; }
            a { color: #64b5f6; }
            table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
            th, td { border: 1px solid #333; padding: 0.5rem; text-align: left; }
            th { background-color: #1e1e1e; }
        </style>
    </head>
    <body>
        <h1>QuickMark Lite</h1>
        <p>Self‑hosted, zero‑login bookmark vault – capture and find links in seconds.</p>
        <h2>Available API Endpoints</h2>
        <table>
            <tr><th>Method</th><th>Path</th><th>Description</th></tr>
            <tr><td>GET</td><td>/health</td><td>Health check</td></tr>
            <tr><td>POST</td><td>/api/bookmarks</td><td>Create a new bookmark (auto‑fetch title)</td></tr>
            <tr><td>GET</td><td>/api/bookmarks</td><td>List bookmarks, optional ?search= term</td></tr>
            <tr><td>GET</td><td>/api/bookmarks/{id}</td><td>Get bookmark by ID</td></tr>
            <tr><td>POST</td><td>/api/bookmarks/preview</td><td>Fetch page title without storing</td></tr>
            <tr><td>POST</td><td>/api/bookmarks/{id}/ai-tags</td><td>Generate AI‑suggested tags (premium)</td></tr>
            <tr><td>GET</td><td>/api/export</td><td>Download all bookmarks as JSON</td></tr>
            <tr><td>POST</td><td>/api/import</td><td>Import bookmarks from JSON</td></tr>
        </table>
        <h2>Tech Stack</h2>
        <ul>
            <li>FastAPI 0.115.0</li>
            <li>SQLAlchemy 2.0.35 (SQLite / PostgreSQL)</li>
            <li>DigitalOcean Serverless Inference (openai‑gpt‑oss‑120b)</li>
            <li>Python 3.12+</li>
        </ul>
        <p>API documentation: <a href="/docs">/docs</a> | <a href="/redoc">/redoc</a></p>
    </body>
    </html>
    """
    return HTMLResponse(content=html, status_code=200)
