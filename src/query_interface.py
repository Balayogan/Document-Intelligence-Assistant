"""
Project: Automated Document & Operational Intelligence System
File: query_interface.py
Description: Main interactive CLI interface for querying unstructured operational and clinical documentation.
Author: Balayogan C (https://github.com/Balayogan)
"""

import os
import time
from typing import List, Dict, Any
from document_processor import DocumentProcessor
from vector_engine import SemanticVectorEngine
from sql_metadata_logger import SQLMetadataLogger

class DocumentIntelligenceAssistant:
    def __init__(self, doc_dir: str = "data/sample_documents", db_path: str = "data/audit_logs.db"):
        self.doc_dir = doc_dir
        self.processor = DocumentProcessor(chunk_size=150, chunk_overlap=30)
        self.engine = SemanticVectorEngine()
        self.logger = SQLMetadataLogger(db_path=db_path)
        self._initialize_knowledge_base()

    def _initialize_knowledge_base(self):
        os.makedirs(self.doc_dir, exist_ok=True)
        files = [f for f in os.listdir(self.doc_dir) if f.endswith(('.txt', '.md'))]
        
        if not files:
            # Seed with representative healthcare and operational reports
            sample_file = os.path.join(self.doc_dir, "clinical_operations_annual_summary.txt")
            with open(sample_file, "w", encoding="utf-8") as f:
                f.write(
                    "Healthwatch Telediagnostics Clinical Operations Annual Review.\n\n"
                    "1. Turnaround Time (TAT) Performance:\n"
                    "Through time-series bottleneck audits and automated Power BI KPI dashboards, "
                    "operational reporting turnaround time was reduced by 28% across 100+ clinical personnel.\n\n"
                    "2. Quality Assurance & Error Audits:\n"
                    "Root-cause investigations into reporting discrepancies achieved an 18% decline in diagnostic deviations. "
                    "First-pass audit accuracy improved from 89% to 96%+ following the introduction of automated weekly scorecards.\n\n"
                    "3. Diagnostic Throughput:\n"
                    "The telemetry operations team processed an average of 350+ weekly ECG deliverables and 180+ Holter continuous "
                    "telemetry streams while sustaining a 95%+ reporting accuracy benchmark.\n\n"
                    "4. Data Pipeline Automation:\n"
                    "Manual reporting efforts were curtailed by 8+ hours per week through scheduled SQL and Excel Power Query ETL pipelines."
                )
            files = [os.path.basename(sample_file)]

        all_chunks = []
        for file_name in files:
            full_path = os.path.join(self.doc_dir, file_name)
            chunks = self.processor.process_file(full_path)
            all_chunks.extend(chunks)

        self.engine.build_index(all_chunks)

    def answer_query(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        start_time = time.time()
        hits = self.engine.search(query, top_k=top_k)
        latency = (time.time() - start_time) * 1000.0

        # Log query metrics in SQL table
        self.logger.log_query(query, hits, latency)

        return {
            "query": query,
            "latency_ms": round(latency, 2),
            "match_count": len(hits),
            "sources": hits
        }

def run_demo():
    print("=" * 70)
    print(" 🤖 Automated Document & Operational Intelligence System")
    print("=" * 70)
    assistant = DocumentIntelligenceAssistant()

    test_queries = [
        "How much was report turnaround time reduced?",
        "What was the improvement in quality discrepancies?",
        "How many hours of manual reporting were saved weekly?",
        "What is the average weekly diagnostic throughput?"
    ]

    for q in test_queries:
        print(f"\n🔎 User Query: '{q}'")
        res = assistant.answer_query(q, top_k=1)
        if res['sources']:
            top = res['sources'][0]
            print(f"✅ Confidence Score: {top['relevance_score'] * 100:.1f}% | Source: {top['doc_name']}")
            print(f"📄 Grounded Evidence: \"{top['content'][:140]}...\"")
        else:
            print("❌ No matching operational evidence found.")
            
    stats = assistant.logger.get_query_analytics_summary()
    print("\n" + "=" * 70)
    print(f"📊 SQL Audit Summary: {stats['total_queries']} queries processed, Avg Latency: {stats['avg_latency_ms']} ms")
    print("=" * 70)

if __name__ == "__main__":
    run_demo()
