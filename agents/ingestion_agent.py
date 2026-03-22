import os
from sentence_transformers import SentenceTransformer
from utils.endee_client import EndeeClient

class IngestionAgent:
    def __init__(self):
        self.client = EndeeClient()
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def ingest_knowledge(self, text: str) -> bool:
        if not text.strip():
            return False
        
        try:
            self.client.ensure_index_exists()
        except Exception:
            pass

        vector = self.model.encode(text).tolist()
        payload = {"text": text}
        try:
            self.client.insert(vector, payload)
            return True
        except Exception as e:
            print(f"Ingestion Error: {e}")
            return False
