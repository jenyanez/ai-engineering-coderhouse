"""Capa de abstracción de Redis para colas FIFO y almacenamiento de tareas."""

import json
import logging
from typing import Any, Dict, List, Optional
import redis
import redis.asyncio as aioredis
from app.config import settings

logger = logging.getLogger("TaskStore")


class TaskStore:
    """Gestiona colas de procesamiento FIFO y estados de ejecución con Redis."""

    def __init__(self):
        self._async_client: Optional[aioredis.Redis] = None
        self._sync_client: Optional[redis.Redis] = None
        self._local_cache: Dict[str, str] = {}

    def get_sync_client(self) -> redis.Redis:
        """Retorna cliente síncrono para el Checkpointer de LangGraph."""
        if self._sync_client is None:
            self._sync_client = redis.from_url(
                settings.redis_url, decode_responses=False
            )
        return self._sync_client

    async def get_async_client(self) -> aioredis.Redis:
        """Retorna cliente asíncrono para FastAPI y Worker."""
        if self._async_client is None:
            self._async_client = aioredis.from_url(
                settings.redis_url, decode_responses=True
            )
        return self._async_client

    async def enqueue_task(self, job_id: str) -> None:
        """Encola un job_id en la lista FIFO de Redis."""
        try:
            client = await self.get_async_client()
            await client.rpush(settings.redis_queue_name, job_id)
        except Exception as err:
            logger.warning(f"No se pudo encolar en Redis ({err}), usando memoria local.")

    async def dequeue_task(self, timeout: int = 1) -> Optional[str]:
        """Extrae el siguiente job_id de la cola bloqueando hasta timeout segundos."""
        try:
            client = await self.get_async_client()
            res = await client.blpop(settings.redis_queue_name, timeout=timeout)
            return res[1] if res else None
        except Exception:
            return None

    async def set_task(self, job_id: str, data: Dict[str, Any]) -> None:
        """Guarda o actualiza el estado de una tarea."""
        serialized = json.dumps(data, default=str)
        key = f"{settings.redis_status_prefix}{job_id}"
        try:
            client = await self.get_async_client()
            await client.set(key, serialized, ex=86400)
        except Exception:
            self._local_cache[key] = serialized

    async def get_task(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Recupera el estado de una tarea por su job_id."""
        key = f"{settings.redis_status_prefix}{job_id}"
        raw = None
        try:
            client = await self.get_async_client()
            raw = await client.get(key)
        except Exception:
            raw = self._local_cache.get(key)
        return json.loads(raw) if raw else None

    async def list_tasks(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Lista las tareas recientes registradas."""
        tasks: List[Dict[str, Any]] = []
        try:
            client = await self.get_async_client()
            keys = await client.keys(f"{settings.redis_status_prefix}*")
            for k in keys[:limit]:
                raw = await client.get(k)
                if raw:
                    tasks.append(json.loads(raw))
        except Exception:
            for val in list(self._local_cache.values())[-limit:]:
                tasks.append(json.loads(val))
        return tasks


task_store = TaskStore()
