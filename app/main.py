from fastapi import FastAPI
from app.scanner import view
from .logging import configure_logging, LogLevels


configure_logging(LogLevels.info)

app = FastAPI(title="Malware Scanner API", version="1.0.0")
app.include_router(view.router)