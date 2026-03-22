import os
from sentence_transformers import SentenceTransformer
from utils.endee_client import EndeeClient
from typing import List, Dict, Any

class SearchAgent:
    def __init__(self):
        self.client = EndeeClient()
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        vector = self.model.encode(query).tolist()
        try:
            results = self.client.search(vector, top_k)
            return results
        except Exception as e:
            print(f"Search Error: {e}")
            return []
