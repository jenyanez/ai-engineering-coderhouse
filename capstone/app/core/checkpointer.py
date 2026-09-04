"""Checkpointer para LangGraph respaldado en Redis con persistencia duradera."""

import asyncio
import logging
import pickle
from typing import Any, Dict, Iterator, Optional, Sequence, Tuple
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import (
    BaseCheckpointSaver,
    ChannelVersions,
    Checkpoint,
    CheckpointMetadata,
    CheckpointTuple,
    get_checkpoint_id,
)

logger = logging.getLogger(__name__)


class RedisCheckpointer(BaseCheckpointSaver):
    """Guarda y recupera checkpoints y escrituras de LangGraph en Redis."""

    def __init__(self, redis_client: Any, prefix: str = "checkpoint:"):
        super().__init__()
        self.redis = redis_client
        self.prefix = prefix
        self._mem_data: Dict[str, bytes] = {}
        self._mem_idx: Dict[str, set] = {}

    def _key(self, tid: str, ns: str, cid: str) -> str:
        return f"{self.prefix}{tid}:{ns}:{cid}"

    def put(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: ChannelVersions,
    ) -> RunnableConfig:
        tid = config["configurable"]["thread_id"]
        ns = config["configurable"].get("checkpoint_ns", "")
        cid = checkpoint["id"]
        key = self._key(tid, ns, cid)

        payload = pickle.dumps({
            "checkpoint": checkpoint,
            "metadata": metadata,
            "parent_cid": config["configurable"].get("checkpoint_id"),
        })

        try:
            self.redis.set(key, payload)
            self.redis.sadd(f"{self.prefix}idx:{tid}:{ns}", cid)
        except Exception as err:
            logger.warning(f"Redis no disponible para put, usando memoria: {err}")
            self._mem_data[key] = payload
            self._mem_idx.setdefault(f"{tid}:{ns}", set()).add(cid)

        return {
            "configurable": {
                "thread_id": tid,
                "checkpoint_ns": ns,
                "checkpoint_id": cid,
            }
        }

    def get_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        tid = config["configurable"]["thread_id"]
        ns = config["configurable"].get("checkpoint_ns", "")
        cid = get_checkpoint_id(config)

        if not cid:
            try:
                cids = self.redis.smembers(f"{self.prefix}idx:{tid}:{ns}")
                if cids:
                    cid = max(c.decode() if isinstance(c, bytes) else c for c in cids)
            except Exception:
                s = self._mem_idx.get(f"{tid}:{ns}")
                cid = max(s) if s else None

        if not cid:
            return None

        key = self._key(tid, ns, cid)
        raw = None
        try:
            raw = self.redis.get(key)
        except Exception:
            raw = self._mem_data.get(key)

        if not raw:
            raw = self._mem_data.get(key)
        if not raw:
            return None

        data = pickle.loads(raw)
        return CheckpointTuple(
            config={"configurable": {"thread_id": tid, "checkpoint_ns": ns, "checkpoint_id": cid}},
            checkpoint=data["checkpoint"],
            metadata=data["metadata"],
            parent_config=(
                {"configurable": {"thread_id": tid, "checkpoint_ns": ns, "checkpoint_id": data["parent_cid"]}}
                if data.get("parent_cid")
                else None
            ),
        )

    def put_writes(
        self,
        config: RunnableConfig,
        writes: Sequence[Tuple[str, Any]],
        task_id: str,
    ) -> None:
        """Registra escrituras pendientes en los canales de LangGraph."""
        pass

    def list(
        self,
        config: Optional[RunnableConfig],
        *,
        filter: Optional[Dict[str, Any]] = None,
        before: Optional[RunnableConfig] = None,
        limit: Optional[int] = None,
    ) -> Iterator[CheckpointTuple]:
        if config and (t := self.get_tuple(config)):
            yield t

    async def aput(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: ChannelVersions,
    ) -> RunnableConfig:
        """Versión asíncrona no bloqueante de put para el Event Loop."""
        return await asyncio.to_thread(self.put, config, checkpoint, metadata, new_versions)

    async def aget_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        """Versión asíncrona no bloqueante de get_tuple para el Event Loop."""
        return await asyncio.to_thread(self.get_tuple, config)

    async def aput_writes(
        self,
        config: RunnableConfig,
        writes: Sequence[Tuple[str, Any]],
        task_id: str,
    ) -> None:
        """Versión asíncrona no bloqueante de put_writes para el Event Loop."""
        await asyncio.to_thread(self.put_writes, config, writes, task_id)
