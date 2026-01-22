from fastapi import FastAPI

from backend.main import app as backend_app


app = FastAPI(title="AWARE AI Content Detection")
app.mount("/", backend_app)

__all__ = ["app"]
