"""Almacenamiento persistente de tareas con Redis y persistencia local en disco."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import redis.asyncio as aioredis

from app.config import settings

logger = logging.getLogger("TaskStore")
_DB_PATH = Path("data/persistent_tasks.json")


class TaskStore:
    """Almacenamiento persistente con Redis y fallback durable en disco JSON."""

    def __init__(self):
        self._memory_db: Dict[str, str] = {}
        self.redis_client: Optional[aioredis.Redis] = None
        self._redis_checked = False
        self._load_from_disk()

    def _load_from_disk(self):
        if _DB_PATH.exists():
            try:
                with open(_DB_PATH, "r", encoding="utf-8") as f:
                    self._memory_db = json.load(f)
            except Exception:
                pass

    def _save_to_disk(self):
        try:
            _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(_DB_PATH, "w", encoding="utf-8") as f:
                json.dump(self._memory_db, f, indent=2)
        except Exception:
            pass

    async def get_client(self) -> Optional[aioredis.Redis]:
        if not self._redis_checked and self.redis_client is None:
            self._redis_checked = True
            try:
                client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
                await client.ping()
                self.redis_client = client
            except Exception as e:
                logger.warning(f"Redis no disponible ({e}). Activando persistencia local en disco.")
        return self.redis_client

    async def set_task(self, job_id: str, data: Dict[str, Any]) -> None:
        client = await self.get_client()
        serialized = json.dumps(data, default=str)
        if client:
            try:
                await client.set(f"task:{job_id}", serialized, ex=settings.JOB_TTL_SECONDS)
                return
            except Exception:
                pass
        self._memory_db[f"task:{job_id}"] = serialized
        self._save_to_disk()

    async def get_task(self, job_id: str) -> Optional[Dict[str, Any]]:
        client, raw = await self.get_client(), None
        if client:
            try:
                raw = await client.get(f"task:{job_id}")
            except Exception:
                pass
        if not raw:
            raw = self._memory_db.get(f"task:{job_id}")
        return json.loads(raw) if raw else None

    async def list_tasks(self, limit: int = 50) -> List[Dict[str, Any]]:
        client, tasks = await self.get_client(), []
        if client:
            try:
                for k in (await client.keys("task:*"))[:limit]:
                    raw = await client.get(k)
                    if raw:
                        tasks.append(json.loads(raw))
                return tasks
            except Exception:
                pass
        for raw in list(self._memory_db.values())[-limit:]:
            tasks.append(json.loads(raw))
        return list(reversed(tasks))


store = TaskStore()
