import os
from fastembed import TextEmbedding
from utils.endee_client import EndeeClient

class IngestionAgent:
    def __init__(self):
        self.client = EndeeClient()
        self.model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

    def ingest_knowledge(self, text: str) -> bool:
        if not text.strip():
            return False
        
        try:
            self.client.ensure_index_exists()
        except Exception:
            pass

        vector = list(self.model.embed([text]))[0].tolist()
        payload = {"text": text}
        try:
            self.client.insert(vector, payload)
            return True
        except Exception as e:
            print(f"Ingestion Error: {e}")
            return False
