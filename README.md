# FactVerifierSystem

## ProjectOverview
This project is a multiagent fact verification platform. It allows users to ingest long-form text (articles or social media posts) into a local knowledge base. The system then evaluates user queries or claims against this knowledge base to determine if they are authentic or fake.

## Architecture
The system employs a multiagent design built in Python. The backend logic is encapsulated within specific agents, and the frontend is provided by a single-page Streamlit application. State is preserved across tabs using Streamlit session state, facilitating the recommendation engine's ability to track user history.

## AgentsAndRoles

### IngestionAgent
Responsible for accepting text inputs, generating dense vector embeddings via a transformer model, and inserting both the embedding and the original text payload into the Endee vector database.

### SearchAgent
Responsible for taking a user query, generating its vector embedding using the same transformer model, and calling the Endee database to perform a vector similarity search to return the top K matching knowledge cards.

### VerificationAgent
Responsible for verifying claims. It receives the user query and the retrieved knowledge cards. It uses the Gemini LLM to analyze the claim strictly within the bounds of the provided context, outputting a structured decision (Authentic, Fake, or InsufficientEvidence).

### RecommendationAgent
Responsible for tracking the last 5 to 6 queries a user has made. It performs repeated search queries against the Endee database to aggregate candidate cards, sorts them by relevance score, and presents the top recommendations back to the user.

## FolderStructure
FactVerifier/
agents/
__init__.py
ingestion_agent.py
search_agent.py
verification_agent.py
recommendation_agent.py
utils/
endee_client.py
app.py
Dockerfile
requirements.txt
.env.example
README.md

## TransformerEmbeddings
Embeddings are created using the sentence-transformers library. Specifically, the all-MiniLM-L6-v2 model is used. This model was chosen because it is practical, runs efficiently locally, and natively integrates with Python without heavy external dependencies.

## EndeeIntegration
Endee is utilized as the core vector database. Our custom EndeeClient wrapper communicates with the Endee HTTP API (assumed default port 8080). When knowledge is ingested, the system transmits the 384-dimensional vector alongside its text payload to be stored.

## GeminiIntegration
We integrate google-generativeai using the gemini-1.5-flash model. Gemini is strictly instructed via a rigid prompt to evaluate the user query only using the injected context cards. It returns a formatted text output summarizing its confidence, reasoning, and cited cards.

## SearchMechanism
Search works by taking the text query, passing it through the same SentenceTransformer model to yield a query vector, and querying Endee's search endpoint. Endee performs vector distance calculations to return the closest matching records.

## VerificationLogic
Verification works by injecting the SearchMechanism results into the Gemini prompt. The prompt includes hard rules forbidding the use of external knowledge. If the provided knowledge cards do not contain relevant information to prove or disprove the claim, the model returns InsufficientEvidence.

## RecommendationLogic
Recommendation works by maintaining a rolling history of the user's queries in the application state. When a recommendation is requested, the RecommendationAgent retrieves the top 2 matches for each of the historical queries, deduplicates them, sorts them globally by similarity score, and returns the top 5 cards.

## EnvironmentVariables
To set environment variables, copy the .env.example file to a new file named .env and populate the required keys.
GEMINI_API_KEY: Your Google Gemini API key.
ENDEE_API_URL: The base URL of your running Endee instance (default: http://localhost:8080/api/v1).

## RunLocally
1. Ensure Python 3.10 or higher is installed.
2. Ensure the Endee vector database is running locally on port 8080.
3. Install dependencies by running: pip install -r requirements.txt
4. Run the Streamlit app: streamlit run app.py

## RunWithDocker
1. Ensure Docker Desktop is installed.
2. Build the image: docker build -t factverifier .
3. Run the container: docker run -p 8501:8501 --env-file .env factverifier
4. Access the application at http://localhost:8501

## AssumptionsAndLimitations
1. The Endee API payload structure is implemented as a standard generic vector database HTTP integration. Depending on the specific Endee compilation, the exact JSON keys for insertion might require minor adjustment.
2. It is assumed the Endee server is actively running before the Python application starts.
3. The sentence-transformers package requires downloading model weights on its first execution, which requires internet access.

## ExactWorkflow
1. Ingestion: User inputs text -> IngestionAgent encodes to 384D vector -> Saved to Endee.
2. Query: User inputs claim -> SearchAgent encodes to 384D query vector -> Endee returns matching cards.
3. Verification: Query and Cards sent to VerificationAgent -> Gemini applies strict rules -> Returns final output.
4. Recommendation: History analyzed -> RecommendationAgent ranks related cards -> Cards presented.
