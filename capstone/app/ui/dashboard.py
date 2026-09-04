"""Router para servir el Mission Control Dashboard de la aplicación."""

import os
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

ui_router = APIRouter(tags=["Mission Control UI"])
_HTML_PATH = os.path.join(os.path.dirname(__file__), "index.html")


@ui_router.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard():
    """Renderiza la consola ejecutiva de control y monitoreo en tiempo real."""
    if os.path.exists(_HTML_PATH):
        with open(_HTML_PATH, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Mission Control Dashboard no disponible</h1>")
