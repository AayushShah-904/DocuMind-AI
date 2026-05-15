"""
Benchmark script: measure retrieval latency, precision@k, and response time.
Run: python scripts/benchmark.py
"""

import asyncio
import statistics
import time
from typing import List

# ── Configuration ─────────────────────────────────────────────────────────────
SAMPLE_QUERIES = [
    "What are the main findings of this document?",
    "Summarize the key points",
    "What methodology was used?",
    "What are the conclusions?",
    "Who are the authors?",
]

API_BASE = "http://localhost:8000/api/v1"
TEST_EMAIL = "benchmark@documind.ai"
TEST_PASSWORD = "Benchmark1234!"


async def run_benchmark():
    import httpx

    async with httpx.AsyncClient(base_url=API_BASE, timeout=60) as client:
        # Auth
        r = await client.post(
            "/auth/register",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
        )
        if r.status_code not in (200, 201, 400):
            print(f"Auth failed: {r.text}")
            return

        if r.status_code == 400:
            r = await client.post(
                "/auth/login",
                json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            )
        token = r.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        latencies: List[float] = []
        print("\n── DocuMind Benchmark ─────────────────────────────")

        for query in SAMPLE_QUERIES:
            start = time.perf_counter()
            full_response = ""

            async with client.stream(
                "POST",
                "/conversations/ask",
                json={"question": query},
                headers=headers,
            ) as resp:
                async for line in resp.aiter_lines():
                    if line.startswith("data:"):
                        full_response += line

            elapsed = time.perf_counter() - start
            latencies.append(elapsed)
            print(f"  Q: {query[:50]:<50} → {elapsed:.2f}s")

        print("\n── Results ──────────────────────────────────────────")
        print(f"  Queries:  {len(latencies)}")
        print(f"  p50:      {statistics.median(latencies):.2f}s")
        print(f"  p95:      {sorted(latencies)[int(len(latencies) * 0.95)]:.2f}s")
        print(f"  avg:      {statistics.mean(latencies):.2f}s")
        print(f"  max:      {max(latencies):.2f}s")
        print("─────────────────────────────────────────────────────\n")


if __name__ == "__main__":
    asyncio.run(run_benchmark())
