"""
bff/src/main.py

Main entrypoint for the BFF FastAPI application.
"""
import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from shared_src.config import settings
from . import chat as chat_router

logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    """Creates and configures the FastAPI application."""
    app = FastAPI(title="AI Excel Interviewer BFF")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  
        allow_credentials=True,
        allow_methods=["*"], 
        allow_headers=["*"],  
    )
    logger.info("CORS enabled for all origins (development mode).")

    app.include_router(chat_router.router, prefix="/api/v1")
    return app

app = create_app()

def cli_main():
    """Entrypoint to run the BFF server."""
    logger.info("Starting BFF server...")
    uvicorn.run(
        "bff.src.main:app",
        host="0.0.0.0",
        port=settings.BFF_PORT_INTERNAL,
    )

if __name__ == "__main__":
    cli_main()