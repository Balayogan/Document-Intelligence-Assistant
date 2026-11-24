"""
Project: Automated Document & Operational Intelligence System
File: vector_engine.py
Description: Vector embeddings, cosine similarity search, and semantic indexing.
Author: Balayogan C (https://github.com/Balayogan)
"""

import numpy as np
from typing import List, Dict, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class SemanticVectorEngine:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            sublinear_tf=True
        )
        self.chunks: List[Dict[str, Any]] = []
        self.matrix = None
        self.is_indexed = False

    def build_index(self, chunks: List[Dict[str, Any]]):
        if not chunks:
            raise ValueError("No chunks provided for vector indexing.")
            
        self.chunks = chunks
        corpus = [c['content'] for c in chunks]
        self.matrix = self.vectorizer.fit_transform(corpus)
        self.is_indexed = True
        print(f"[INDEXED] Successfully indexed {len(chunks)} chunks with vocabulary size {self.matrix.shape[1]}.")

    def search(self, query: str, top_k: int = 3, threshold: float = 0.10) -> List[Dict[str, Any]]:
        if not self.is_indexed:
            raise RuntimeError("Index has not been built. Call build_index() first.")
            
        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.matrix).flatten()
        
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            if score >= threshold:
                chunk = self.chunks[idx].copy()
                chunk['relevance_score'] = round(score, 4)
                results.append(chunk)
                
        return results

if __name__ == "__main__":
    from document_processor import DocumentProcessor
    dp = DocumentProcessor(chunk_size=50, chunk_overlap=10)
    docs = [
        "Clinical turnaround time was reduced by 28% through automated Power BI dashboards.",
        "SQL queries utilized common table expressions and window functions for technician audit scorecards.",
        "Customer churn was predicted with 0.89 ROC-AUC and 0.86 F1-score using gradient boosting algorithms."
    ]
    all_chunks = []
    for i, d in enumerate(docs):
        all_chunks.extend(dp.chunk_text(d, f"DOC_{i+1}", f"sample_{i+1}.txt"))
        
    engine = SemanticVectorEngine()
    engine.build_index(all_chunks)
    
    query = "How much was turnaround time reduced?"
    hits = engine.search(query, top_k=2)
    print(f"\nQuery: '{query}'")
    for hit in hits:
        print(f"-> Score: {hit['relevance_score']} | Source: {hit['doc_name']} | Content: {hit['content']}")
