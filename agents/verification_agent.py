import os
import requests
from typing import List, Dict, Any

GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1/models"
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

class VerificationAgent:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        self.model = GEMINI_MODEL

    def _call_gemini(self, prompt: str) -> str:
        url = f"{GEMINI_ENDPOINT}/{self.model}:generateContent?key={self.api_key}"
        body = {"contents": [{"parts": [{"text": prompt}]}]}
        resp = requests.post(url, json=body)
        if not resp.ok:
            raise Exception(f"{resp.status_code} {resp.text}")
        data = resp.json()
        return data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")

    def build_prompt(self, query: str, context_cards: List[Dict[str, Any]]) -> str:
        context_str = "\n\n".join([f"CARD {i+1}: {card.get('payload', {}).get('text', '')}" for i, card in enumerate(context_cards)])
        return f"""
You are a strict fact-checking assistant. Your ONLY job is to verify the query based on the provided KNOWLEDGE CARDS.

RULES:
1. You must only use the retrieved knowledge cards as evidence.
2. You must not use pretrained world knowledge.
3. You must not infer beyond the evidence.
4. If evidence is weak or conflicting or non-existent, return InsufficientEvidence.
5. You must formulate your response EXACTLY in the structured format requested below.

QUERY: {query}

KNOWLEDGE CARDS:
{context_str}

Respond EXACTLY in this format:
Decision:
[Authentic, Fake, or InsufficientEvidence]

Confidence:
[Low, Medium, or High]

EvidenceSummary:
[Short summary based only on retrieved cards]

Reasoning:
[Short explanation grounded only in the retrieved cards]

CitedKnowledgeCards:
[List of the top retrieved cards used in the judgment (e.g. CARD 1, CARD 2)]
"""

    def verify(self, query: str, context_cards: List[Dict[str, Any]]) -> str:
        if not context_cards:
            return "Decision:\nInsufficientEvidence\n\nConfidence:\nLow\n\nEvidenceSummary:\nNo context cards found.\n\nReasoning:\nCannot verify without knowledge base context.\n\nCitedKnowledgeCards:\nNone"
        prompt = self.build_prompt(query, context_cards)
        try:
            return self._call_gemini(prompt)
        except Exception as e:
            return f"Decision:\nInsufficientEvidence\n\nConfidence:\nLow\n\nEvidenceSummary:\nError connecting to Verification LLM.\n\nReasoning:\n{str(e)}\n\nCitedKnowledgeCards:\nNone"
