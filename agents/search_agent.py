import os
from fastembed import TextEmbedding
from utils.endee_client import EndeeClient
from typing import List, Dict, Any

class SearchAgent:
    def __init__(self):
        self.client = EndeeClient()
        self.model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        vector = list(self.model.embed([query]))[0].tolist()
        try:
            results = self.client.search(vector, top_k)
            return results
        except Exception as e:
            print(f"Search Error: {e}")
            return []
