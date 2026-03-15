"""
MechForge AI — Daily Knowledge Agent
=====================================
每天自动为用户生成并推送机械工程领域的：
  - 失效案例速览
  - 重要行业标准摘要
  - 工程计算技巧
  - 行业新闻动态
  - 工具/软件使用提示
  - 材料洞察

架构：
  APScheduler（AsyncIOScheduler）驱动 → 复用应用 LLM 配置生成内容
  → 写入 daily_feed.json → FastAPI 路由 /api/daily 提供给前端
  → 前端 toast 通知 + 侧边栏展示

接入方式：
  在 server.py 里 import 并注册：
      from gui_pywebview.daily_agent import DailyAgent, router as daily_router
      app.include_router(daily_router)
      daily_agent = DailyAgent()
      @app.on_event("startup")
      async def _start_agent():
          await daily_agent.start()
"""

from __future__ import annotations

import asyncio
import json
import logging
import random
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path

import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import APIRouter

logger = logging.getLogger("mechforge.daily_agent")

# ── 路径 ─────────────────────────────────────────────────────
AGENT_DIR = Path(__file__).parent.resolve()
FEED_FILE = AGENT_DIR / "daily_feed.json"
HISTORY_FILE = AGENT_DIR / "daily_history.json"

# ── FastAPI 路由 ──────────────────────────────────────────────
router = APIRouter(prefix="/api/daily", tags=["daily-agent"])


@router.get("")
async def get_daily_feed():
    """GET /api/daily — 返回今日推送内容"""
    if not FEED_FILE.exists():
        return {"date": str(date.today()), "items": [], "status": "pending", "gen_id": None}
    try:
        data = json.loads(FEED_FILE.read_text(encoding="utf-8"))
        return data
    except Exception as e:
        logger.error(f"读取 feed 失败: {e}")
        return {"date": str(date.today()), "items": [], "status": "error", "gen_id": None}


@router.get("/history")
async def get_feed_history(days: int = 7):
    """GET /api/daily/history — 返回近 N 天的推送历史"""
    if not HISTORY_FILE.exists():
        return {"history": []}
    try:
        history: list[dict] = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        cutoff = str(date.today() - timedelta(days=days))
        recent = [h for h in history if h.get("date", "") >= cutoff]
        recent.sort(key=lambda h: h.get("date", ""), reverse=True)
        return {"history": recent}
    except Exception as e:
        logger.error(f"读取历史记录失败: {e}")
        return {"history": []}


@router.get("/history/{target_date}")
async def get_feed_by_date(target_date: str):
    """GET /api/daily/history/{date} — 获取指定日期的推送内容"""
    if not HISTORY_FILE.exists():
        return {"date": target_date, "items": [], "status": "not_found"}
    try:
        history: list[dict] = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        for h in history:
            if h.get("date") == target_date and h.get("items"):
                return h
        return {"date": target_date, "items": [], "status": "not_found"}
    except Exception as e:
        logger.error(f"读取历史推送失败: {e}")
        return {"date": target_date, "items": [], "status": "error"}


_daily_agent_instance: DailyAgent | None = None


def set_daily_agent(agent: DailyAgent) -> None:
    global _daily_agent_instance
    _daily_agent_instance = agent


@router.post("/refresh")
async def manual_refresh():
    """POST /api/daily/refresh — 手动触发一次内容生成"""
    global _daily_agent_instance
    if _daily_agent_instance is None:
        return {"status": "error", "message": "agent not started"}
    gen_id = str(uuid.uuid4())[:8]
    asyncio.create_task(_daily_agent_instance.refresh(gen_id=gen_id))
    return {"status": "queued", "gen_id": gen_id, "message": "refresh signal sent"}


# ══════════════════════════════════════════════════════════════
#  内容提示词模板
# ══════════════════════════════════════════════════════════════

PROMPT_TEMPLATES: list[dict[str, str]] = [
    {
        "type": "failure_case",
        "type_cn": "失效案例",
        "icon": "⚠",
        "severity": "warning",
        "prompt": (
            "请生成一个真实的机械工程失效案例速览，包含：\n"
            "1. 案例标题（10~20字，要有具体零部件名称）\n"
            "2. 故障现象（2~3句）\n"
            "3. 根本原因（2~3句，要有技术术语）\n"
            "4. 核心预防措施（3条，每条一句话）\n"
            "5. 相关标准或参考（1条，格式：标准编号+名称）\n\n"
            "领域随机选择：疲劳断裂、磨损失效、腐蚀失效、装配失效、热处理缺陷、密封失效、振动失效之一\n"
            "严格按 JSON 输出，不要有 markdown 代码块，字段：title, phenomenon, root_cause, prevention(list[str]), reference"
        ),
    },
    {
        "type": "standard_spotlight",
        "type_cn": "标准速览",
        "icon": "📋",
        "severity": "info",
        "prompt": (
            "请介绍一个对机械工程师有实际价值的国际或国家标准，包含：\n"
            "1. 标准编号和全称\n"
            "2. 核心适用场景（1~2句）\n"
            "3. 最重要的技术要求或公式（2~3条，可以包含数值）\n"
            "4. 工程师最常用到的查询点（2条）\n"
            "5. 获取方式（官方网址）\n\n"
            "从以下领域随机选择一个标准：ISO/ASME/GB/DIN/VDI/API/AWS/ASTM 任意一个机械类标准\n"
            "严格按 JSON 输出，字段：std_no, std_name, scope, key_requirements(list[str]), query_points(list[str]), source_url"
        ),
    },
    {
        "type": "calc_tip",
        "type_cn": "计算技巧",
        "icon": "🔢",
        "severity": "tip",
        "prompt": (
            "请提供一个机械工程计算的实用技巧或快速估算方法，包含：\n"
            "1. 技巧标题\n"
            "2. 适用场景（一句话）\n"
            "3. 核心公式或方法（含变量说明）\n"
            "4. 快速数值估算示例（给出具体数字）\n"
            "5. 注意事项和适用范围\n\n"
            "话题可选：轴承寿命估算、螺栓预紧力计算、疲劳寿命估算、齿轮强度校核、热变形量估算、压力容器壁厚计算、焊缝强度、弹簧设计等\n"
            "严格按 JSON 输出，字段：title, scenario, formula, example, notes"
        ),
    },
    {
        "type": "tool_tip",
        "type_cn": "工具技巧",
        "icon": "🛠",
        "severity": "tip",
        "prompt": (
            "请介绍机械工程师常用的一个软件工具或工程技巧，包含：\n"
            "1. 工具/技巧名称\n"
            "2. 主要用途（1~2句）\n"
            "3. 核心操作步骤（3~4步）\n"
            "4. 一个容易踩的坑\n"
            "5. 官网或文档链接\n\n"
            "可选工具：ANSYS、SolidWorks、CATIA、Abaqus、MATLAB、FreeCAD、OpenFOAM、COMSOL、Simscale、KISSsoft 等\n"
            "严格按 JSON 输出，字段：name, purpose, steps(list[str]), pitfall, doc_url"
        ),
    },
    {
        "type": "material_insight",
        "type_cn": "材料洞察",
        "icon": "🔬",
        "severity": "info",
        "prompt": (
            "请介绍一种机械工程常用材料的关键性能与选用要点，包含：\n"
            "1. 材料牌号和中文名称\n"
            "2. 核心力学性能（3个关键参数，含数值范围）\n"
            "3. 最适合的应用场景（2~3个具体零件）\n"
            "4. 选用时的注意事项（2条）\n"
            "5. 等效国际牌号对照（至少列出中/美/欧 3个）\n\n"
            "随机从以下选择：结构钢、不锈钢、铸铁、铝合金、钛合金、工程塑料、复合材料、弹簧钢、轴承钢、工具钢 之一\n"
            "严格按 JSON 输出，字段：grade, name_cn, properties(list[str]), applications(list[str]), notes(list[str]), equivalents(dict)"
        ),
    },
    {
        "type": "industry_news",
        "type_cn": "行业动态",
        "icon": "📰",
        "severity": "info",
        "prompt": (
            "请基于你的训练知识，描述机械工程领域的一个重要技术趋势或行业动态，包含：\n"
            "1. 动态标题\n"
            "2. 核心内容概述（3~4句）\n"
            "3. 对工程师的实际影响（2条）\n"
            "4. 相关技术关键词（3~5个）\n"
            "5. 建议关注的方向\n\n"
            "可选话题：增材制造进展、数字孪生应用、智能检测技术、绿色制造、工业4.0、轻量化材料、高熵合金、工业机器人精度提升等\n"
            "严格按 JSON 输出，字段：headline, summary, impacts(list[str]), keywords(list[str]), outlook"
        ),
    },
]

RENDER_SCHEMA: dict[str, list[str]] = {
    "failure_case": ["title", "phenomenon", "root_cause", "prevention", "reference"],
    "standard_spotlight": [
        "std_no", "std_name", "scope", "key_requirements", "query_points", "source_url",
    ],
    "calc_tip": ["title", "scenario", "formula", "example", "notes"],
    "tool_tip": ["name", "purpose", "steps", "pitfall", "doc_url"],
    "material_insight": ["grade", "name_cn", "properties", "applications", "notes", "equivalents"],
    "industry_news": ["headline", "summary", "impacts", "keywords", "outlook"],
}


# ══════════════════════════════════════════════════════════════
#  LLM 客户端适配器（复用应用配置）
# ══════════════════════════════════════════════════════════════


class LLMAdapter:
    """
    统一调用 LLM。优先使用应用已有配置（从 state 读取），
    支持 Ollama / OpenAI / Anthropic / GGUF。
    """

    def __init__(self, config: dict | None = None):
        self._cfg = config or {}
        self._resolved = False
        self._provider: str = ""
        self._model: str = ""
        self._api_key: str = ""
        self._base_url: str = ""

    def _resolve_config(self) -> None:
        """从应用 state 读取实际 LLM 配置（延迟解析）"""
        if self._resolved:
            return
        self._resolved = True

        # 如果外部显式指定了 provider 和 api_key，直接使用
        if self._cfg.get("provider") and self._cfg.get("api_key"):
            self._provider = self._cfg["provider"]
            self._model = self._cfg.get("model", "")
            self._api_key = self._cfg.get("api_key", "")
            self._base_url = self._cfg.get("base_url", "")
            return

        # 否则从应用全局 state 自动检测
        try:
            from api.state import state

            # GGUF 本地模型
            if state.current_provider == "gguf" and state.gguf_llm is not None:
                self._provider = "gguf"
                self._model = state.gguf_model_path or "gguf-local"
                logger.info("DailyAgent 使用 GGUF 本地模型")
                return

            # 从配置中读取 active provider
            provider_name = state.config.provider.get_active_provider()
            provider_config = state.config.provider.get_config(provider_name)

            if provider_name == "ollama":
                self._provider = "ollama"
                self._base_url = getattr(provider_config, "url", "http://localhost:11434")
                self._model = getattr(
                    provider_config, "model",
                    getattr(provider_config, "llm_model", "qwen2.5:3b"),
                )
                logger.info("DailyAgent 使用 Ollama: %s @ %s", self._model, self._base_url)

            elif provider_name in ("openai", "anthropic"):
                self._provider = provider_name
                self._api_key = getattr(provider_config, "api_key", "")
                self._model = getattr(provider_config, "model", "")
                self._base_url = getattr(
                    provider_config, "base_url",
                    getattr(provider_config, "url", ""),
                )
                logger.info("DailyAgent 使用 %s: %s", provider_name, self._model)

            else:
                # 默认回退到 Ollama
                self._provider = "ollama"
                self._base_url = "http://localhost:11434"
                self._model = "qwen2.5:3b"
                logger.info("DailyAgent 回退到 Ollama 默认配置")

        except Exception as e:
            logger.warning("无法从 state 读取 LLM 配置，回退到 Ollama: %s", e)
            self._provider = "ollama"
            self._base_url = "http://localhost:11434"
            self._model = "qwen2.5:3b"

    def get_provider_info(self) -> dict[str, str]:
        """返回当前使用的 provider 信息"""
        self._resolve_config()
        return {
            "provider": self._provider,
            "model": self._model,
            "base_url": self._base_url,
        }

    async def generate(self, prompt: str) -> str:
        """返回模型的原始文本输出"""
        self._resolve_config()

        if self._provider == "gguf":
            return await self._gguf(prompt)
        elif self._provider == "ollama":
            return await self._ollama(prompt)
        elif self._provider == "openai":
            return await self._openai(prompt)
        elif self._provider == "anthropic":
            return await self._anthropic(prompt)
        else:
            raise ValueError(f"未知 provider: {self._provider}")

    async def _gguf(self, prompt: str) -> str:
        from api.state import state

        if state.gguf_llm is None:
            raise RuntimeError("GGUF 模型未加载")

        messages = [
            {
                "role": "system",
                "content": "你是一名资深机械工程师，擅长故障分析、标准解读和工程计算。只输出 JSON，不要有任何额外文字。",
            },
            {"role": "user", "content": prompt},
        ]

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: state.gguf_llm.create_chat_completion(
                messages=messages,
                max_tokens=1024,
                temperature=0.7,
            ),
        )
        return result["choices"][0]["message"]["content"] if result.get("choices") else ""

    async def _ollama(self, prompt: str) -> str:
        url = self._base_url or "http://localhost:11434"
        model = self._model or "qwen2.5:3b"
        payload = {
            "model": model,
            "prompt": (
                "你是一名资深机械工程师，擅长故障分析、标准解读和工程计算。"
                "只输出 JSON，不要有任何额外文字。\n\n" + prompt
            ),
            "stream": False,
            "options": {"temperature": 0.7, "num_predict": 1024},
        }
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(f"{url}/api/generate", json=payload)
            resp.raise_for_status()
            return resp.json().get("response", "")

    async def _openai(self, prompt: str) -> str:
        api_key = self._api_key
        if not api_key:
            raise RuntimeError("OpenAI API Key 未配置")
        model = self._model or "gpt-4o-mini"
        base_url = self._base_url or "https://api.openai.com"
        base_url = base_url.rstrip("/")
        if not base_url.endswith("/v1"):
            base_url += "/v1"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一名资深机械工程师，擅长故障分析、标准解读和工程计算。只输出 JSON，不要有任何额外文字。",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
            "max_tokens": 1024,
        }
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{base_url}/chat/completions", headers=headers, json=payload,
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]

    async def _anthropic(self, prompt: str) -> str:
        api_key = self._api_key
        if not api_key:
            raise RuntimeError("Anthropic API Key 未配置")
        model = self._model or "claude-haiku-4-5-20251001"
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": model,
            "max_tokens": 1024,
            "system": "你是一名资深机械工程师，擅长故障分析、标准解读和工程计算。只输出 JSON，不要有任何额外文字。",
            "messages": [{"role": "user", "content": prompt}],
        }
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages", headers=headers, json=payload,
            )
            resp.raise_for_status()
            return resp.json()["content"][0]["text"]


# ══════════════════════════════════════════════════════════════
#  内容生成 & 解析
# ══════════════════════════════════════════════════════════════


def _parse_json(raw: str) -> dict | None:
    """从 LLM 输出中提取 JSON，容忍 markdown 代码块包裹"""
    raw = raw.strip()
    for fence in ("```json", "```"):
        if raw.startswith(fence):
            raw = raw[len(fence):]
            break
    if raw.endswith("```"):
        raw = raw[:-3]
    raw = raw.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(raw[start: end + 1])
            except json.JSONDecodeError:
                pass
    return None


async def generate_item(
    llm: LLMAdapter,
    tmpl: dict,
    today_str: str,
    retry: int = 2,
) -> dict | None:
    """调用 LLM 生成一条推送内容并解析，失败时最多重试 retry 次"""
    for attempt in range(retry + 1):
        try:
            raw = await llm.generate(tmpl["prompt"])
            data = _parse_json(raw)
            if data:
                return {
                    "id": f"{today_str}_{tmpl['type']}",
                    "type": tmpl["type"],
                    "type_cn": tmpl["type_cn"],
                    "icon": tmpl["icon"],
                    "severity": tmpl["severity"],
                    "data": data,
                    "generated_at": datetime.now().isoformat(timespec="seconds"),
                    "schema": RENDER_SCHEMA.get(tmpl["type"], []),
                }
            else:
                logger.warning(
                    "[%s] JSON 解析失败 (attempt %d), raw[:200]=%s",
                    tmpl["type"], attempt + 1, raw[:200],
                )
        except Exception as e:
            logger.error("[%s] LLM 调用失败 (attempt %d): %s", tmpl["type"], attempt + 1, e)
        if attempt < retry:
            await asyncio.sleep(2)
    return None


# ══════════════════════════════════════════════════════════════
#  DailyAgent 主类
# ══════════════════════════════════════════════════════════════


class DailyAgent:
    """
    每日知识更新 Agent。

    用法（在 server.py startup 里）：
        agent = DailyAgent()
        await agent.start()
    """

    def __init__(self, config: dict | None = None):
        self._cfg = config or {}
        self._llm = LLMAdapter(self._cfg)
        self._scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")
        self._running = False
        self._manual_mode = self._cfg.get("manual_mode", True)
        self._generating = False

    @property
    def is_generating(self) -> bool:
        return self._generating

    async def start(self) -> None:
        if self._manual_mode:
            self._running = True
            logger.info("Daily Agent 已启动（手动模式，等待用户触发）")
        else:
            hour = int(self._cfg.get("schedule_hour", 7))
            minute = int(self._cfg.get("schedule_minute", 0))

            self._scheduler.add_job(
                self._daily_job,
                trigger=CronTrigger(hour=hour, minute=minute),
                id="daily_update",
                replace_existing=True,
                misfire_grace_time=3600,
            )
            self._scheduler.start()
            self._running = True
            logger.info(f"Daily Agent 已启动，每天 {hour:02d}:{minute:02d} 触发")

            if not self._today_done():
                logger.info("今日内容尚未生成，立即执行...")
                asyncio.create_task(self._daily_job())

    async def stop(self) -> None:
        if self._running:
            if not self._manual_mode:
                self._scheduler.shutdown(wait=False)
            self._running = False

    async def refresh(self, gen_id: str | None = None) -> dict:
        """手动触发（供 API 端点调用），gen_id 用于前端轮询区分新旧内容"""
        return await self._daily_job(gen_id=gen_id, force=True)

    # ── 内部逻辑 ──────────────────────────────────────────────

    def _today_done(self) -> bool:
        if not FEED_FILE.exists():
            return False
        try:
            data = json.loads(FEED_FILE.read_text(encoding="utf-8"))
            return data.get("date") == str(date.today()) and bool(data.get("items"))
        except Exception:
            return False

    async def _daily_job(self, gen_id: str | None = None, force: bool = False) -> dict:
        """核心任务：生成今日内容并写入文件"""
        if self._generating:
            return {"status": "busy", "message": "正在生成中，请稍候"}

        self._generating = True
        today = str(date.today())
        n_items = int(self._cfg.get("items_per_day", 3))
        n_items = max(1, min(n_items, len(PROMPT_TEMPLATES)))

        if gen_id is None:
            gen_id = str(uuid.uuid4())[:8]

        # 写入 generating 状态，让前端知道正在生成
        progress_feed = {
            "date": today,
            "gen_id": gen_id,
            "items": [],
            "status": "generating",
            "total": 0,
            "target": n_items,
            "provider": self._llm.get_provider_info(),
        }
        FEED_FILE.write_text(
            json.dumps(progress_feed, ensure_ascii=False, indent=2), encoding="utf-8",
        )

        logger.info("[%s] 开始生成每日推送 (%d 条)...", today, n_items)

        try:
            # 随机选取（force 模式不检查历史）
            if force:
                candidates = PROMPT_TEMPLATES
            else:
                used_types = self._load_recent_types()
                candidates = [t for t in PROMPT_TEMPLATES if t["type"] not in used_types]
                if len(candidates) < n_items:
                    candidates = PROMPT_TEMPLATES

            selected = random.sample(candidates, min(n_items, len(candidates)))

            items = []
            errors: list[str] = []
            for i, tmpl in enumerate(selected):
                logger.info("  生成 [%d/%d]: %s", i + 1, n_items, tmpl["type_cn"])

                # 更新进度
                progress_feed["status"] = "generating"
                progress_feed["progress"] = {
                    "current": i + 1,
                    "total": n_items,
                    "current_type": tmpl["type_cn"],
                }
                progress_feed["items"] = items
                FEED_FILE.write_text(
                    json.dumps(progress_feed, ensure_ascii=False, indent=2), encoding="utf-8",
                )

                item = await generate_item(self._llm, tmpl, today)
                if item:
                    items.append(item)
                    logger.info("  ✓ %s 生成成功", tmpl["type_cn"])
                    progress_feed["items"] = items
                    progress_feed["total"] = len(items)
                    FEED_FILE.write_text(
                        json.dumps(progress_feed, ensure_ascii=False, indent=2),
                        encoding="utf-8",
                    )
                else:
                    errors.append(tmpl["type_cn"])
                    logger.warning("  ✗ %s 生成失败，跳过", tmpl["type_cn"])

            feed = {
                "date": today,
                "gen_id": gen_id,
                "generated_at": datetime.now().isoformat(timespec="seconds"),
                "items": items,
                "status": "ok" if items else "failed",
                "total": len(items),
                "provider": self._llm.get_provider_info(),
            }
            if errors:
                feed["errors"] = errors

            FEED_FILE.write_text(
                json.dumps(feed, ensure_ascii=False, indent=2), encoding="utf-8",
            )
            self._save_history(today, [t["type"] for t in selected], items)
            logger.info("[%s] 每日推送完成，共 %d 条", today, len(items))
            return feed

        except Exception as e:
            logger.error("[%s] 每日推送生成异常: %s", today, e)
            error_feed = {
                "date": today,
                "gen_id": gen_id,
                "items": [],
                "status": "failed",
                "total": 0,
                "error_detail": str(e),
                "provider": self._llm.get_provider_info(),
            }
            FEED_FILE.write_text(
                json.dumps(error_feed, ensure_ascii=False, indent=2), encoding="utf-8",
            )
            return error_feed

        finally:
            self._generating = False

    def _load_recent_types(self) -> set[str]:
        """读取近 7 天已推送过的类型，避免重复"""
        if not HISTORY_FILE.exists():
            return set()
        try:
            history: list[dict] = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
            cutoff = str(date.today() - timedelta(days=7))
            recent = [h for h in history if h.get("date", "") >= cutoff]
            return {t for h in recent for t in h.get("types", [])}
        except Exception:
            return set()

    def _save_history(self, today: str, types: list[str], items: list[dict]) -> None:
        """保存今日推送记录（含生成内容摘要，供历史浏览）"""
        try:
            existing: list[dict] = []
            if HISTORY_FILE.exists():
                existing = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))

            cutoff = str(date.today() - timedelta(days=30))
            existing = [h for h in existing if h.get("date", "") >= cutoff]

            # 用相同日期的最新记录替换旧的
            existing = [h for h in existing if h.get("date") != today]

            entry = {
                "date": today,
                "types": types,
                "generated_at": datetime.now().isoformat(timespec="seconds"),
                "total": len(items),
                "items": items,
            }
            existing.append(entry)

            HISTORY_FILE.write_text(
                json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8",
            )
        except Exception as e:
            logger.warning("保存历史记录失败: %s", e)
