"""
ChangeGuardian AI — Neo4j Graph Client
DO NOT MODIFY.
"""
from __future__ import annotations

import logging
from typing import Any

from neo4j import AsyncGraphDatabase, AsyncDriver

from core import load_config

logger = logging.getLogger(__name__)


class Neo4jClient:
    _driver: AsyncDriver | None = None

    def __init__(self) -> None:
        cfg = load_config().get("neo4j", {})
        self._uri = cfg.get("uri", "bolt://localhost:7687")
        self._user = cfg.get("user", "neo4j")
        self._password = cfg.get("password", "password")
        self._seed = str(cfg.get("seed_demo_data", "true")).lower() == "true"

    async def connect(self) -> None:
        self._driver = AsyncGraphDatabase.driver(self._uri, auth=(self._user, self._password))
        logger.info("Neo4j connected — %s", self._uri)

    async def close(self) -> None:
        if self._driver:
            await self._driver.close()
            logger.info("Neo4j connection closed")

    async def query(self, cypher: str, params: dict[str, Any] | None = None) -> list[dict]:
        if not self._driver:
            await self.connect()
        async with self._driver.session() as session:
            result = await session.run(cypher, params or {})
            return [record.data() async for record in result]

    async def find_dependencies(self, service_name: str) -> list[str]:
        rows = await self.query(
            "MATCH (s {name: $name})-[:CALLS|USES|DEPENDS_ON*1..3]->(dep) "
            "RETURN DISTINCT dep.name AS name",
            {"name": service_name},
        )
        return [r["name"] for r in rows if r.get("name")]

    async def find_incidents_for_services(self, names: list[str]) -> list[dict]:
        return await self.query(
            "MATCH (i:Incident)-[:CAUSED]->(s) WHERE s.name IN $names "
            "RETURN i.id AS id, i.title AS title, i.severity AS severity, "
            "i.root_cause AS root_cause, collect(s.name) AS impacted_services "
            "ORDER BY i.severity DESC LIMIT 20",
            {"names": names},
        )

    async def seed_demo_data(self) -> None:
        if not self._seed:
            return
        await self.query("""
            MERGE (ps:Service {name: 'payment-service'})
            MERGE (os:Service {name: 'order-service'})
            MERGE (us:Service {name: 'user-service'})
            MERGE (ns:Service {name: 'notification-service'})
            MERGE (pg:Database {name: 'postgres-payments'})
            MERGE (rd:Database {name: 'redis-cache'})
            MERGE (pa:API    {name: 'payment-gateway-api'})
            MERGE (ps)-[:CALLS]->(pa)
            MERGE (ps)-[:USES]->(pg)
            MERGE (ps)-[:USES]->(rd)
            MERGE (os)-[:CALLS]->(ps)
            MERGE (os)-[:DEPENDS_ON]->(us)
            MERGE (ns)-[:DEPENDS_ON]->(os)
            MERGE (i1:Incident {id:'INC-001', title:'Payment timeout spike',
                severity:'HIGH', root_cause:'payment-service v3.9 memory leak'})
            MERGE (i2:Incident {id:'INC-002', title:'Order cascade failure',
                severity:'CRITICAL', root_cause:'payment-service outage propagated to order-service'})
            MERGE (i3:Incident {id:'INC-003', title:'Redis cache stampede',
                severity:'MEDIUM', root_cause:'Cold start after redis-cache restart caused thundering herd'})
            MERGE (i1)-[:CAUSED]->(ps)
            MERGE (i2)-[:CAUSED]->(os)
            MERGE (i2)-[:CAUSED]->(ps)
            MERGE (i3)-[:CAUSED]->(ps)
            MERGE (i3)-[:CAUSED]->(rd)
        """)
        logger.info("Neo4j demo data seeded")


neo4j_client = Neo4jClient()
