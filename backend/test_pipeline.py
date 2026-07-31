import asyncio

from app.agents.orchestrator import run_pipeline


async def test():
    await run_pipeline("INC-2026-041")


asyncio.run(test())
