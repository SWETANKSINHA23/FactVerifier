import requests
import json
import os
from typing import List, Dict, Any

class EndeeClient:
    def __init__(self):
        self.base_url = os.getenv("ENDEE_API_URL", "http://localhost:8080/api/v1")
        self.index_name = "knowledge_base"

    def ensure_index_exists(self):
        res = requests.get(f"{self.base_url}/index/list")
        if res.status_code == 200:
            indexes = res.json().get("indexes", [])
            if self.index_name not in indexes:
                requests.post(f"{self.base_url}/index/create", json={"name": self.index_name, "dimension": 384})

    def insert(self, vector: List[float], payload: Dict[str, Any]):
        url = f"{self.base_url}/index/insert"
        data = {
            "index": self.index_name,
            "vector": vector,
            "payload": payload
        }
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()

    def search(self, vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/index/search"
        data = {
            "index": self.index_name,
            "vector": vector,
            "top_k": top_k
        }
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json().get("results", [])
