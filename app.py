import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from agents.ingestion_agent import IngestionAgent
from agents.search_agent import SearchAgent
from agents.verification_agent import VerificationAgent
from agents.recommendation_agent import RecommendationAgent

st.set_page_config(page_title="FactVerifier API", layout="wide")

if "query_history" not in st.session_state:
    st.session_state.query_history = []

@st.cache_resource
def get_agents():
    return {
        "ingest": IngestionAgent(),
        "search": SearchAgent(),
        "verify": VerificationAgent(),
        "recommend": RecommendationAgent()
    }

agents = get_agents()

st.title("FactVerifier Multiagent System")

tab1, tab2, tab3 = st.tabs(["KnowledgeBuilder", "SearchEngine", "RecommendationEngine"])

with tab1:
    st.header("Knowledge Builder")
    text_input = st.text_area("Paste article, tweet, or fact to ingest:", height=150)
    if st.button("Ingest Knowledge"):
        if text_input:
            with st.spinner("Ingesting and embedding..."):
                success = agents["ingest"].ingest_knowledge(text_input)
                if success:
                    st.success("Successfully ingested into Endee database.")
                else:
                    st.error("Failed to ingest. Make sure Endee is running on localhost:8080.")
        else:
            st.warning("Please enter text before ingesting.")

with tab2:
    st.header("Search Engine & Verification")
    query_input = st.text_input("Enter a claim to verify:")
    if st.button("Verify Claim"):
        if query_input:
            st.session_state.query_history.append(query_input)
            st.session_state.query_history = st.session_state.query_history[-6:]
            
            with st.spinner("Retrieving knowledge..."):
                matches = agents["search"].search(query_input, top_k=3)
                
            st.subheader("Top Matches found in DB")
            if not matches:
                st.info("No matching knowledge found.")
            else:
                for i, m in enumerate(matches):
                    st.markdown(f"**Match {i+1}**: {m.get('payload', {}).get('text', '')}")
            
            with st.spinner("Verifying with Gemini..."):
                verdict = agents["verify"].verify(query_input, matches)
            
            st.subheader("Final Verification Report")
            st.text(verdict)
        else:
            st.warning("Please enter a claim.")

with tab3:
    st.header("Recommendation Engine")
    if st.button("Get Recommendations"):
        if not st.session_state.query_history:
            st.info("No query history available for recommendations.")
        else:
            with st.spinner("Generating recommendations..."):
                recs = agents["recommend"].get_recommendations(st.session_state.query_history)
                if not recs:
                    st.info("No recommendations found.")
                else:
                    for i, r in enumerate(recs):
                        st.markdown(f"**Recommendation {i+1}**: {r.get('payload', {}).get('text', '')}")
