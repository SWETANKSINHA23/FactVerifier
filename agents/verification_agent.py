import os
import google.generativeai as genai
from typing import List, Dict, Any

class VerificationAgent:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))
        self.model = genai.GenerativeModel('gemini-1.5-flash')

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
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Decision:\nInsufficientEvidence\n\nConfidence:\nLow\n\nEvidenceSummary:\nError connecting to Verification LLM.\n\nReasoning:\n{str(e)}\n\nCitedKnowledgeCards:\nNone"
