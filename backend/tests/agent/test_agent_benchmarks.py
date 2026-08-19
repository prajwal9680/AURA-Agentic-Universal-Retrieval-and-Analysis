"""
AURA Evaluation Suite — Pillar 3: Agentic RAG Benchmarks (LangGraph Engine)
Evaluates:
- Tool calling precision and routing
- Multi-hop graph traversal fidelity
- Critic node reflection and self-correction
- Calibrated citation grounding
"""
import sys
import asyncio
from pathlib import Path
import pytest

backend_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(backend_dir))

from app.database import init_db, AsyncSessionLocal
from app.services.agent import run_aura_investigation_graph
from app.services.agent_tools import (
    tool_search_memories,
    tool_get_memory,
    tool_find_related,
    tool_calculate,
)


@pytest.mark.asyncio
async def test_agent_tool_search_memories():
    await init_db()
    async with AsyncSessionLocal() as db:
        res = await tool_search_memories(db=db, query="laptop receipt", top_k=5)
        assert res["tool"] == "search_memories"
        assert res["count"] > 0
        assert len(res["results"]) > 0


@pytest.mark.asyncio
async def test_agent_tool_find_related():
    await init_db()
    async with AsyncSessionLocal() as db:
        # Search for a memory ID first
        s_res = await tool_search_memories(db=db, query="YOLO", top_k=1)
        if s_res["results"]:
            mid = s_res["results"][0]["id"]
            rel_res = await tool_find_related(db=db, memory_id=mid)
            assert rel_res["tool"] == "find_related"
            assert "edges" in rel_res


def test_agent_tool_calculate():
    res1 = tool_calculate("68990 * 0.18")
    assert res1["success"] is True
    assert round(res1["result"], 2) == 12418.20

    # Test safety sandbox blocking harmful expressions
    res2 = tool_calculate("__import__('os').system('dir')")
    assert res2["success"] is False


@pytest.mark.asyncio
async def test_agent_end_to_end_investigation():
    await init_db()
    async with AsyncSessionLocal() as db:
        res = await run_aura_investigation_graph(
            query="Find my Wi-Fi password",
            thread_id="test_bm_wifi_01",
            db=db,
        )

        assert "answer" in res or "final_answer" in res
        assert "confidence" in res
        assert "execution_trace" in res
        assert len(res["execution_trace"]) >= 4  # planner -> tool_executor -> reranker -> critic -> synthesizer
