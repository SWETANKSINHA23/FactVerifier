import requests
import json
import os
import uuid
import msgpack
from typing import List, Dict, Any

class EndeeClient:
    def __init__(self):
        self.base_url = os.getenv("ENDEE_API_URL", "http://localhost:8080/api/v1")
        self.index_name = "knowledge_base"

    def ensure_index_exists(self):
        res = requests.get(f"{self.base_url}/index/list")
        if res.status_code == 200:
            data = res.json()
            indexes = [idx.get("name") for idx in data.get("indexes", [])]
            if self.index_name not in indexes:
                requests.post(f"{self.base_url}/index/create", json={
                    "index_name": self.index_name,
                    "dim": 384,
                    "space_type": "cosine",
                    "M": 16,
                    "ef_con": 200,
                    "precision": "int16"
                })

    def insert(self, vector: List[float], payload: Dict[str, Any]):
        url = f"{self.base_url}/index/{self.index_name}/vector/insert"
        data = {
            "id": str(uuid.uuid4()),
            "vector": vector,
            "meta": json.dumps(payload)
        }
        response = requests.post(url, json=data)
        response.raise_for_status()
        return {"status": "success"}

    def search(self, vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/index/{self.index_name}/search"
        data = {
            "k": top_k,
            "vector": vector
        }
        response = requests.post(url, json=data)
        response.raise_for_status()
        
        parsed = msgpack.unpackb(response.content, raw=False)
        
        if len(parsed) == 2 and isinstance(parsed[0], list) and (len(parsed[0]) == 0 or (len(parsed[0]) > 0 and isinstance(parsed[0][0], list))):
            dense_results = parsed[0]
        else:
            dense_results = parsed
        
        results = []
        for r in dense_results:
            try:
                if not isinstance(r, list) or len(r) < 3:
                    continue
                similarity = r[0]
                meta_bytes = r[2]
                if isinstance(meta_bytes, bytes):
                    meta_bytes = meta_bytes.decode('utf-8')
                payload = json.loads(meta_bytes) if meta_bytes else {}
                
                results.append({
                    "score": similarity,
                    "payload": payload
                })
            except Exception as e:
                print(f"Parse error: {e}")
                
        return results
