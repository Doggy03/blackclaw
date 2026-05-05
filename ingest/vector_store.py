"""向量库适配层：首选 Chroma 持久化；未安装时使用空操作并记录告警。"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

_logger = logging.getLogger(__name__)

try:
    import chromadb

    _CHROMA_AVAILABLE = True
except ImportError:
    chromadb = None  # type: ignore[assignment]
    _CHROMA_AVAILABLE = False


def _sanitize_metadata(md: dict[str, Any]) -> dict[str, str | int | float | bool]:
    """
    将元数据规整为 Chroma 接受的标量类型。

    Args:
        md: 原始键值。

    Returns:
        可被 Chroma 写入的精简字典。
    """

    out: dict[str, str | int | float | bool] = {}
    for k, v in md.items():
        if isinstance(v, (str, int, float, bool)):
            out[str(k)] = v
        elif v is None:
            out[str(k)] = ""
        else:
            out[str(k)] = str(v)
    return out


class VectorMemory:
    """
    结构化行情快照的向量入库封装。

    安装向量依赖：``pip install -r requirements-vectors.txt``
    """

    def __init__(self, config_path: Path | None = None) -> None:
        """
        Args:
            config_path: ``vector_store.yaml`` 路径。
        """

        root = Path(__file__).resolve().parents[1]
        self._config_path = config_path or (root / "config" / "vector_store.yaml")
        self._root = root
        self._persist_dir: Path = root / ".chroma" / "ironclaw"
        self._collection_name: str = "black_metal_basis"
        self._load_yaml()

        self._client: Any | None = None
        if _CHROMA_AVAILABLE:
            self._persist_dir.mkdir(parents=True, exist_ok=True)
            self._client = chromadb.PersistentClient(path=str(self._persist_dir))

    def _load_yaml(self) -> None:
        """从 YAML 覆盖默认集合名与持久化目录。"""
        if not self._config_path.exists():
            _logger.warning("Missing %s; using builtin defaults.", self._config_path)
            return
        raw = yaml.safe_load(self._config_path.read_text(encoding="utf-8")) or {}
        chroma = raw.get("chroma") or {}
        persist = chroma.get("persist_directory")
        if persist:
            self._persist_dir = (self._root / Path(persist)).resolve()
        if chroma.get("collection"):
            self._collection_name = str(chroma["collection"])

    @property
    def collection_name(self) -> str:
        """当前 Chroma collection 名称。"""

        return self._collection_name

    @property
    def persist_directory(self) -> Path:
        """Chroma 持久化路径。"""

        return self._persist_dir

    def upsert_market_snapshot(self, *, doc_id: str, document: str, metadata: dict[str, Any]) -> bool:
        """
        写入或覆盖一条市场行情文档（Chroma 可用时真实写入）。

        Args:
            doc_id: 文档唯一 id。
            document: 供嵌入的自由文本快照。
            metadata: 与文档一同存储的筛选字段。

        Returns:
            ``True`` 表示已写入向量库；``False`` 表示跳过（通常为未安装 chromadb）。
        """

        if self._client is None:
            return False
        md = dict(metadata)
        md.setdefault("indexed_at", datetime.now(tz=UTC).isoformat())
        coll = self._client.get_or_create_collection(self._collection_name)
        coll.upsert(ids=[doc_id], documents=[document], metadatas=[_sanitize_metadata(md)])
        return True
