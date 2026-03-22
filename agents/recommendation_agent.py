from agents.search_agent import SearchAgent
from typing import List, Dict, Any

class RecommendationAgent:
    def __init__(self):
        self.search_agent = SearchAgent()

    def get_recommendations(self, previous_queries: List[str]) -> List[Dict[str, Any]]:
        if not previous_queries:
            return []
            
        all_candidates = []
        for query in previous_queries:
            results = self.search_agent.search(query, top_k=2)
            all_candidates.extend(results)
            
        unique_matches = {}
        for match in all_candidates:
            text = match.get("payload", {}).get("text")
            if text and text not in unique_matches:
                unique_matches[text] = match

        sorted_matches = sorted(
            list(unique_matches.values()), 
            key=lambda x: x.get("score", 0), 
            reverse=True
        )
        return sorted_matches[:5]
