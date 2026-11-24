"""
Project: Automated Document & Operational Intelligence System
File: sql_metadata_logger.py
Description: SQLite-backed operational audit logging for query tracking, latency metrics, and document citations.
Author: Balayogan C (https://github.com/Balayogan)
"""

import sqlite3
import datetime
from typing import List, Dict, Any

class SQLMetadataLogger:
    def __init__(self, db_path: str = "data/audit_logs.db"):
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS query_audit_logs (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query_text TEXT NOT NULL,
                    results_count INTEGER NOT NULL,
                    top_source_doc TEXT,
                    max_relevance_score REAL,
                    latency_ms REAL NOT NULL,
                    queried_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS document_metadata (
                    doc_id TEXT PRIMARY KEY,
                    doc_name TEXT NOT NULL,
                    total_chunks INTEGER NOT NULL,
                    indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()

    def log_query(self, query: str, hits: List[Dict[str, Any]], latency_ms: float):
        top_source = hits[0]['doc_name'] if hits else "None"
        max_score = hits[0]['relevance_score'] if hits else 0.0
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO query_audit_logs 
                (query_text, results_count, top_source_doc, max_relevance_score, latency_ms)
                VALUES (?, ?, ?, ?, ?);
            """, (query, len(hits), top_source, max_score, round(latency_ms, 2)))
            conn.commit()

    def get_query_analytics_summary(self) -> Dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_queries,
                    AVG(latency_ms) as avg_latency_ms,
                    AVG(results_count) as avg_results_returned,
                    COUNT(DISTINCT top_source_doc) as unique_sources_cited
                FROM query_audit_logs;
            """)
            row = cursor.fetchone()
            return {
                "total_queries": row[0],
                "avg_latency_ms": round(row[1] or 0.0, 2),
                "avg_results_returned": round(row[2] or 0.0, 2),
                "unique_sources_cited": row[3]
            }

if __name__ == "__main__":
    logger = SQLMetadataLogger()
    sample_hits = [{"doc_name": "operations_q3.txt", "relevance_score": 0.88}]
    logger.log_query("What was the TAT reduction?", sample_hits, latency_ms=14.2)
    stats = logger.get_query_analytics_summary()
    print(f"[SQL AUDIT METRICS] {stats}")
