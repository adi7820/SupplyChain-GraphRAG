
from typing import Iterable
from typing import Any
from neo4j import GraphDatabase, Driver
from ..config import Config, get_config
import logging

log = logging.getLogger(__name__)

class GraphUnavailable(RuntimeError):
    """Neo4j is not reachable, with an actionable message attached."""

class GraphClient:
    def __init__(self, config: Config | None = None) -> None:
        self.config = config or get_config()
        settings = self.config.neo4j
        self.database = settings.database
        self._driver: Driver = GraphDatabase.driver(
            settings.uri, auth=(settings.user, settings.password)
        )

    def run(self, cypher: str, **params: Any) -> list[dict[str, Any]]:
        with self._driver.session(database=self.database) as session:
            result = session.run(cypher, parameters=params)
            return [record.data() for record in result]

    def run_wrtie(self, cypher: str, **params:Any) -> list[dict[str, Any]]:
        with self._driver.session(database=self.database) as session:
            return session.execute_write(lambda tx: [r.data() for r in tx.run(cypher, parameters=params)])

    def run_batch(self, cypher: str, rows: Iterable[dict[str, Any]], batch_size: int = 500) -> int:
        rows = list(rows)
        written = 0
        for start in range(0, len(rows), batch_size):
            chunk = rows[start:start+batch_size]
            self.run_write(cypher, rows=chunk)
            written += len(chunk)
        return written
