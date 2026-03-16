"""
Obsidian 同步服务
将 Obsidian Vault 中的笔记同步到 RAG 知识库
"""

import json
import re
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import logging

logger = logging.getLogger("mechforge.api.obsidian")

# 同步状态记录文件
SYNC_STATE_FILE = Path("data/obsidian_sync_state.json")


class ObsidianSyncService:
    """Obsidian Vault 同步服务"""

    def __init__(self, vault_path: str):
        self.vault = Path(vault_path)
        self.state = self._load_state()

    # ── 状态持久化 ─────────────────────────────────────────────────────────

    def _load_state(self) -> dict:
        """加载同步状态"""
        if SYNC_STATE_FILE.exists():
            try:
                return json.loads(SYNC_STATE_FILE.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {"synced_files": {}}

    def _save_state(self):
        """保存同步状态"""
        SYNC_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        SYNC_STATE_FILE.write_text(
            json.dumps(self.state, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    def _file_hash(self, path: Path) -> str:
        """计算文件 MD5 哈希"""
        return hashlib.md5(path.read_bytes()).hexdigest()

    # ── PULL: Obsidian → MechForge RAG ───────────────────────────────────

    async def pull(self, subfolder: str = "") -> dict:
        """扫描 vault，把新增/修改的笔记入库"""
        from .knowledge_engine import get_knowledge_engine, _chunk_text

        if not self.vault.exists():
            return {"error": "Vault 路径不存在", "new": 0, "updated": 0, "skipped": 0, "failed": 0}

        search_root = self.vault / subfolder if subfolder else self.vault
        md_files = list(search_root.rglob("*.md"))

        results = {"new": 0, "updated": 0, "skipped": 0, "failed": 0, "files": []}

        # 获取 RAG 引擎
        try:
            engine = get_knowledge_engine()
            engine._ensure_ready()
        except Exception as e:
            logger.error(f"知识库引擎未就绪: {e}")
            return {"error": f"知识库引擎未就绪: {e}", **results}

        for md_path in md_files:
            rel = str(md_path.relative_to(self.vault))
            current_hash = self._file_hash(md_path)
            prev = self.state["synced_files"].get(rel, {})

            # 未变化则跳过
            if prev.get("hash") == current_hash:
                results["skipped"] += 1
                continue

            try:
                # 解析 markdown 内容
                content = self._parse_markdown(md_path)
                if not content or len(content.strip()) < 50:
                    continue

                # 提取元数据
                metadata = {
                    "title": md_path.stem,
                    "source": "obsidian",
                    "vault_path": rel,
                    "links": self._extract_links(content),
                    "synced_at": datetime.now().isoformat(),
                }

                # 切片
                chunks = _chunk_text(content)
                if not chunks:
                    continue

                # 生成 ID
                fhash = current_hash[:8]
                ids = [f"obsidian_{md_path.stem}_{i}_{fhash}" for i in range(len(chunks))]
                metadatas = [
                    {**metadata, "chunk_index": i, "total_chunks": len(chunks)}
                    for i in range(len(chunks))
                ]

                # 移除旧文档（如果存在）
                old_prefix = f"obsidian_{md_path.stem}_"
                try:
                    existing = engine._collection.get()
                    if existing and existing.get("ids"):
                        old_ids = [id for id in existing["ids"] if id.startswith(old_prefix)]
                        if old_ids:
                            engine._collection.delete(ids=old_ids)
                except Exception:
                    pass

                # 添加新文档
                batch_size = 50
                for start in range(0, len(chunks), batch_size):
                    end = min(start + batch_size, len(chunks))
                    engine._collection.add(
                        ids=ids[start:end],
                        documents=chunks[start:end],
                        metadatas=metadatas[start:end],
                    )

                is_update = bool(prev)
                self.state["synced_files"][rel] = {
                    "hash": current_hash,
                    "synced_at": datetime.now().isoformat(),
                    "title": metadata["title"],
                }
                results["updated" if is_update else "new"] += 1
                results["files"].append({
                    "path": rel,
                    "title": metadata["title"],
                    "action": "updated" if is_update else "new",
                    "chunks": len(chunks)
                })

            except Exception as e:
                logger.error(f"同步文件失败 {rel}: {e}")
                results["failed"] += 1
                results["files"].append({"path": rel, "error": str(e)})

        self._save_state()
        return results

    # ── PUSH: MechForge → Obsidian ───────────────────────────────────────

    async def push(
        self,
        content: str,
        title: str,
        tags: list[str] = None,
        target_folder: str = "MechForge",
    ) -> dict:
        """把 AI 生成的内容写入 Obsidian 笔记"""
        tags = tags or []

        folder = self.vault / target_folder
        folder.mkdir(parents=True, exist_ok=True)

        # 文件名：标题去掉非法字符
        safe_title = re.sub(r'[\\/:*?"<>|]', "_", title)
        note_path = folder / f"{safe_title}.md"

        # 如果同名文件存在，追加而不是覆盖
        if note_path.exists():
            existing = note_path.read_text(encoding="utf-8")
            final_content = (
                existing.rstrip()
                + "\n\n---\n\n"
                + f"**MechForge 补充** · {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
                + content
            )
            action = "appended"
        else:
            # 新建笔记，带 frontmatter
            tag_str = "\n".join(f"  - {t}" for t in tags) if tags else ""
            final_content = (
                f"---\n"
                f"title: {title}\n"
                f"created: {datetime.now().strftime('%Y-%m-%d')}\n"
                f"source: MechForge AI\n"
                + (f"tags:\n{tag_str}\n" if tag_str else "")
                + f"---\n\n{content}"
            )
            action = "created"

        note_path.write_text(final_content, encoding="utf-8")
        return {
            "success": True,
            "path": str(note_path.relative_to(self.vault)),
            "action": action,
        }

    # ── 工具方法 ─────────────────────────────────────────────────────────

    def _parse_markdown(self, path: Path) -> str:
        """解析 markdown 文件，尝试提取纯文本"""
        try:
            # 尝试使用 frontmatter
            try:
                import frontmatter
                post = frontmatter.load(path)
                return post.content.strip()
            except ImportError:
                pass

            # 回退：直接读取文件
            content = path.read_text(encoding="utf-8")

            # 移除 frontmatter（如果存在）
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    content = parts[2]

            return content.strip()
        except Exception as e:
            logger.warning(f"解析 markdown 失败 {path}: {e}")
            return ""

    def _extract_links(self, content: str) -> list[str]:
        """提取 [[双链]] 中的页面引用"""
        return re.findall(r"\[\[([^\]|#]+)", content)

    def get_vault_tree(self) -> dict:
        """返回 vault 的文件夹结构，供前端渲染"""
        if not self.vault.exists():
            return {}

        tree = {}
        for f in self.vault.rglob("*.md"):
            parts = f.relative_to(self.vault).parts
            node = tree
            for part in parts[:-1]:
                node = node.setdefault(part, {})
            node[parts[-1]] = str(f.relative_to(self.vault))
        return tree

    def get_status(self) -> dict:
        """获取 vault 状态"""
        if not self.vault.exists():
            return {
                "vault_path": str(self.vault),
                "accessible": False,
                "total_notes": 0,
                "synced_notes": 0,
                "unsynced_notes": 0,
            }

        md_files = list(self.vault.rglob("*.md"))
        synced = len(self.state["synced_files"])

        return {
            "vault_path": str(self.vault),
            "accessible": True,
            "total_notes": len(md_files),
            "synced_notes": synced,
            "unsynced_notes": len(md_files) - synced,
        }


# ── 获取服务实例 ─────────────────────────────────────────────────────────

_obsidian_service: Optional[ObsidianSyncService] = None


def get_obsidian_service(vault_path: str = None) -> ObsidianSyncService:
    """获取 Obsidian 同步服务实例"""
    global _obsidian_service

    if vault_path:
        _obsidian_service = ObsidianSyncService(vault_path)
    elif _obsidian_service is None:
        # 从配置中获取 vault 路径
        try:
            from .state import state
            if hasattr(state, "config") and hasattr(state.config, "knowledge"):
                config = state.config.knowledge
                if hasattr(config, "obsidian_vault_path"):
                    vault_path = config.obsidian_vault_path
        except Exception:
            pass

        if not vault_path:
            raise ValueError("未配置 Obsidian Vault 路径")

        _obsidian_service = ObsidianSyncService(vault_path)

    return _obsidian_service


def reset_obsidian_service():
    """重置服务实例"""
    global _obsidian_service
    _obsidian_service = None
