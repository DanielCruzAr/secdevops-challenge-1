from fastapi import FastAPI
from app.scanner import view
from .logging import configure_logging, LogLevels
from app.config.vt_client import client


configure_logging(LogLevels.info)

app = FastAPI(title="Malware Scanner API", version="1.0.0")
app.include_router(view.router)

@app.on_event("shutdown")
async def shutdown_event():
    """
    Cleanup VT client on application shutdown.
    """
    await client.close_async()
    