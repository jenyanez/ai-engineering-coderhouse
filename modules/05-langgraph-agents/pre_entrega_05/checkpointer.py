"""
Pre-entrega 5: Agente de Razonamiento Cíclico con Memoria Persistente
Archivo: checkpointer.py — Fase 3: Persistencia con SqliteSaver

Configura el checkpointer SqliteSaver para persistir el estado
del agente en un archivo SQLite local (checkpoints.db).
Esto permite que el agente recuerde interacciones previas
al reanudar con el mismo thread_id.

Nota: Se usa AsyncSqliteSaver (variante asíncrona de SqliteSaver)
porque el agente ejecuta en entorno asíncrono (asyncio / ainvoke).
Se expone como context manager para gestionar correctamente la conexión.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import aiosqlite
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver


@asynccontextmanager
async def get_checkpointer(
    db_path: str = "checkpoints.db",
) -> AsyncGenerator[AsyncSqliteSaver, None]:
    """
    Context manager asíncrono que crea y gestiona un AsyncSqliteSaver.

    Args:
        db_path: Ruta al archivo SQLite de checkpoints.

    Yields:
        Instancia de AsyncSqliteSaver conectada y lista para usar.
    """
    async with aiosqlite.connect(db_path) as conn:
        saver = AsyncSqliteSaver(conn)
        await saver.setup()
        yield saver
