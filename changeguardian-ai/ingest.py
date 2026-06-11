"""
ChangeGuardian AI — Data Ingestion Script

Seeds Neo4j with the graph model and indexes documents
into the configured vector store.

Usage:
  python ingest.py                # seed Neo4j + index documents
  python ingest.py --neo4j-only   # only seed Neo4j
  python ingest.py --docs-only    # only index documents

Documents go in:  data/documents/
Supported types:  .txt  .pdf  .md  .json  .csv  (set in config.yaml)
"""
import argparse
import asyncio
import json
import logging
from pathlib import Path

from core import load_config, setup_logging
from core.graph_client import neo4j_client

logger = logging.getLogger(__name__)


async def seed_graph() -> None:
    logger.info("Connecting to Neo4j…")
    await neo4j_client.connect()
    await neo4j_client.seed_demo_data()

    # Optionally load supplemental incident data from data/incidents/
    incidents_path = Path("data/incidents/sample_incidents.json")
    if incidents_path.exists():
        incidents = json.loads(incidents_path.read_text())
        for inc in incidents:
            await neo4j_client.query(
                "MERGE (i:Incident {id: $id}) "
                "SET i.title=$title, i.severity=$severity, i.root_cause=$root_cause",
                {k: inc.get(k, "") for k in ["id", "title", "severity", "root_cause"]},
            )
        logger.info("Loaded %d incidents from sample_incidents.json", len(incidents))

    await neo4j_client.close()
    logger.info("Graph seeding complete.")


def index_documents() -> None:
    """
    Chunk, embed, and store documents from data/documents/.

    Currently a scaffold — integrate your FAISS or Pinecone
    embedding pipeline here based on config.yaml > vector_store.
    """
    cfg = load_config()
    docs_cfg = cfg.get("documents", {})
    docs_path = Path(docs_cfg.get("path", "data/documents"))
    supported = set(docs_cfg.get("supported_extensions", [".txt", ".md", ".json"]))

    if not docs_path.exists():
        logger.warning("Documents path '%s' does not exist — skipping", docs_path)
        return

    eligible = [f for f in docs_path.rglob("*") if f.is_file() and f.suffix in supported]
    if not eligible:
        logger.info("No documents found in '%s'", docs_path)
        return

    vs_type = cfg.get("vector_store", {}).get("type", "faiss")
    logger.info("Vector store: %s | Indexing %d document(s)…", vs_type, len(eligible))
    for doc in eligible:
        logger.info("  • %s", doc.relative_to(docs_path))
    logger.info("Document indexing complete. (Plug in FAISS/Pinecone embedding here.)")


async def main() -> None:
    setup_logging()
    parser = argparse.ArgumentParser(description="ChangeGuardian AI — Ingest data")
    parser.add_argument("--neo4j-only", action="store_true", help="Only seed Neo4j")
    parser.add_argument("--docs-only", action="store_true", help="Only index documents")
    args = parser.parse_args()

    if args.docs_only:
        index_documents()
    elif args.neo4j_only:
        await seed_graph()
    else:
        await seed_graph()
        index_documents()


if __name__ == "__main__":
    asyncio.run(main())
