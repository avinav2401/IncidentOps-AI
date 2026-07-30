from app.agents.orchestrator import run_pipeline
import asyncio

async def test():
    await run_pipeline('INC-2026-041')

asyncio.run(test())
