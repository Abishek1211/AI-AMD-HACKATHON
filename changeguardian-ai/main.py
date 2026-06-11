"""
ChangeGuardian AI — CLI Entry Point

Usage:
  python main.py                          # demo mode — runs example queries
  python main.py -q "upgrade payment..."  # single query
  python main.py -i                       # interactive chat mode
  python main.py --serve                  # start FastAPI server
  python main.py -q "..." --verbose       # print full JSON result
"""
import argparse
import asyncio
import json
import sys

from core import setup_logging
from core.graph_client import neo4j_client
from core.orchestrator import run_pipeline

DEMO_QUERIES = [
    "Upgrade payment-service from v4.0 to v4.2",
    "Add invoice_metadata JSONB column to the payments table in postgres-payments",
    "Scale order-service from 3 to 10 replicas in the EU region",
]


async def _run_single(query: str, verbose: bool = False) -> None:
    print(f"\nAnalysing: {query}")
    print("─" * 64)
    result = await run_pipeline(query)

    if not result.get("guardrail_passed", True):
        print(f"[BLOCKED]  {result.get('guardrail_reason')}")
        return

    print(f"  Route         : {result.get('route', 'n/a')}")
    print(f"  Risk Score    : {result.get('risk_score', 0)} / 100")
    print(f"  Confidence    : {result.get('confidence', 0)} %")
    print(f"  Impact Level  : {result.get('impact_level', 'unknown')}")
    print(f"  Recommendation: {result.get('recommendation', 'n/a')}")
    print(f"  Justification : {result.get('justification', '')}")
    print(f"  Explanation   : {result.get('explanation', '')}")
    if verbose:
        print("\nFull result:")
        print(json.dumps(result, indent=2, default=str))


async def _interactive() -> None:
    print("ChangeGuardian AI — Interactive Mode  (Ctrl+C to quit)\n")
    while True:
        try:
            query = input("Change request > ").strip()
            if not query:
                continue
            await _run_single(query)
        except (KeyboardInterrupt, EOFError):
            print("\nBye!")
            break


async def _demo() -> None:
    print("ChangeGuardian AI — Demo Mode\n")
    for query in DEMO_QUERIES:
        await _run_single(query)


async def main() -> None:
    setup_logging()

    parser = argparse.ArgumentParser(description="ChangeGuardian AI")
    parser.add_argument("-q", "--query", help="Single change request to analyse")
    parser.add_argument("-i", "--interactive", action="store_true", help="Interactive mode")
    parser.add_argument("-v", "--verbose", action="store_true", help="Print full JSON result")
    parser.add_argument("--serve", action="store_true", help="Start FastAPI server")
    args = parser.parse_args()

    if args.serve:
        import uvicorn
        from api.server import app
        from core import load_config
        cfg = load_config().get("api", {})
        uvicorn.run(app, host=cfg.get("host", "0.0.0.0"), port=int(cfg.get("port", 8000)))
        return

    await neo4j_client.connect()
    await neo4j_client.seed_demo_data()
    try:
        if args.query:
            await _run_single(args.query, args.verbose)
        elif args.interactive:
            await _interactive()
        else:
            await _demo()
    finally:
        await neo4j_client.close()


if __name__ == "__main__":
    asyncio.run(main())
