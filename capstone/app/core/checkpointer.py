"""Checkpointer para LangGraph respaldado en Redis con persistencia duradera."""

import json
import logging
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
    """Guarda y recupera checkpoints de LangGraph en Redis."""

    def __init__(self, redis_client: Any, prefix: str = "checkpoint:"):
        super().__init__()
        self.redis = redis_client
        self.prefix = prefix
        self._memory_fallback: Dict[str, Dict[str, Any]] = {}

    def _key(self, thread_id: str, checkpoint_ns: str, checkpoint_id: str) -> str:
        return f"{self.prefix}{thread_id}:{checkpoint_ns}:{checkpoint_id}"

    def put(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: ChannelVersions,
    ) -> RunnableConfig:
        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
        cid = checkpoint["id"]
        key = self._key(thread_id, checkpoint_ns, cid)

        data = {
            "checkpoint": self.serde.dumps_typed(checkpoint),
            "metadata": self.serde.dumps_typed(metadata),
            "parent_checkpoint_id": config["configurable"].get("checkpoint_id"),
        }

        try:
            # Serializar diccionario a formato seguro en Redis
            serialized = json.dumps(
                {k: v.decode("latin1") if isinstance(v, bytes) else v for k, v in data.items()}
            )
            self.redis.set(key, serialized)
            self.redis.sadd(f"{self.prefix}index:{thread_id}:{checkpoint_ns}", cid)
        except Exception as err:
            logger.warning(f"Redis no disponible para put checkpoint, usando fallback: {err}")
            self._memory_fallback[key] = data

        return {
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_ns": checkpoint_ns,
                "checkpoint_id": cid,
            }
        }

    def get_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
        cid = get_checkpoint_id(config)

        if not cid:
            try:
                cids = self.redis.smembers(f"{self.prefix}index:{thread_id}:{checkpoint_ns}")
                if cids:
                    cid = max(c.decode() if isinstance(c, bytes) else c for c in cids)
            except Exception:
                matching = [
                    k.split(":")[-1]
                    for k in self._memory_fallback
                    if k.startswith(f"{self.prefix}{thread_id}:{checkpoint_ns}:")
                ]
                cid = max(matching) if matching else None

        if not cid:
            return None

        key = self._key(thread_id, checkpoint_ns, cid)
        raw_data = None
        try:
            val = self.redis.get(key)
            if val:
                raw = json.loads(val.decode() if isinstance(val, bytes) else val)
                raw_data = {
                    k: v.encode("latin1") if isinstance(v, str) else v for k, v in raw.items()
                }
        except Exception:
            raw_data = self._memory_fallback.get(key)

        if not raw_data:
            return None

        checkpoint = self.serde.loads_typed(raw_data["checkpoint"])
        metadata = self.serde.loads_typed(raw_data["metadata"])
        parent_cid = raw_data.get("parent_checkpoint_id")

        return CheckpointTuple(
            config={"configurable": {"thread_id": thread_id, "checkpoint_ns": checkpoint_ns, "checkpoint_id": cid}},
            checkpoint=checkpoint,
            metadata=metadata,
            parent_config={"configurable": {"thread_id": thread_id, "checkpoint_ns": checkpoint_ns, "checkpoint_id": parent_cid}} if parent_cid else None,
        )

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
