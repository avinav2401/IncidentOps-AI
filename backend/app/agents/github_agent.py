"""Simulated GitHub Commit Agent."""

import asyncio


async def fetch_recent_commits(service: str) -> list[str]:
    """
    Simulates a GitHub Agent fetching recent commits for the affected service.
    """
    await asyncio.sleep(1)  # Simulate API delay
    return [
        "Commit a1b2c3d: Increased DB pool size limit.",
        "Commit f5e6d7c: Updated dependencies.",
        "Commit 9a8b7c6: Refactored payment processing logic."
    ]
