"""
Project: Automated Document & Operational Intelligence System
File: document_processor.py
Description: Text extraction, data normalization, and semantic chunking with metadata tagging.
Author: Balayogan C (https://github.com/Balayogan)
"""

import os
import re
from typing import List, Dict, Any

class DocumentProcessor:
    def __init__(self, chunk_size: int = 300, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def clean_text(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)
        return text.strip()

    def chunk_text(self, text: str, doc_id: str, doc_name: str) -> List[Dict[str, Any]]:
        cleaned = self.clean_text(text)
        words = cleaned.split()
        
        chunks = []
        start_idx = 0
        chunk_idx = 1
        
        while start_idx < len(words):
            end_idx = min(start_idx + self.chunk_size, len(words))
            chunk_content = " ".join(words[start_idx:end_idx])
            
            chunks.append({
                "chunk_id": f"{doc_id}_c{chunk_idx}",
                "doc_id": doc_id,
                "doc_name": doc_name,
                "chunk_index": chunk_idx,
                "word_count": len(words[start_idx:end_idx]),
                "content": chunk_content
            })
            
            if end_idx == len(words):
                break
                
            start_idx += (self.chunk_size - self.chunk_overlap)
            chunk_idx += 1
            
        return chunks

    def process_file(self, file_path: str) -> List[Dict[str, Any]]:
        doc_name = os.path.basename(file_path)
        doc_id = os.path.splitext(doc_name)[0]
        
        if file_path.endswith('.txt') or file_path.endswith('.md'):
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
        else:
            raise ValueError(f"Unsupported file format: {file_path}")
            
        return self.chunk_text(text, doc_id, doc_name)

if __name__ == "__main__":
    processor = DocumentProcessor(chunk_size=100, chunk_overlap=20)
    sample_text = (
        "Healthwatch Telemetry Operations Report Q3 2023. "
        "During this period, technician review turnaround time improved by 28% "
        "following the deployment of the automated KPI dashboard. "
        "Quality discrepancy audits revealed an 18% decline in classification defects across 100+ personnel. "
        "Total weekly diagnostic volume averaged 350+ ECG records and 180+ Holter continuous monitoring streams."
    )
    chunks = processor.chunk_text(sample_text, "DOC_001", "operations_report_q3.txt")
    print(f"Processed into {len(chunks)} chunk(s):")
    for c in chunks:
        print(f"[{c['chunk_id']}] ({c['word_count']} words): {c['content'][:80]}...")
