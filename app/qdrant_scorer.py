import os
import numpy as np
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import uuid

load_dotenv()

EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
VECTOR_DIM = EMBEDDING_MODEL.get_sentence_embedding_dimension()

qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

COLLECTION = "candidates"

if not qdrant_client.collection_exists(COLLECTION):
    qdrant_client.create_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=VECTOR_DIM, distance=Distance.COSINE)
    )

def calculate_similarity(text_a, text_b):
    if not text_a or not text_b:
        return 0
    embeddings = EMBEDDING_MODEL.encode([text_a, text_b])
    similarity = np.dot(embeddings[0], embeddings[1])
    return int(np.clip(similarity * 100, 1, 100))

def get_vector_scores(ideal_candidate_profile, candidate_resume, 
                      task_description, code_description):
    resume_fit_score = calculate_similarity(ideal_candidate_profile, candidate_resume)
    code_fit_score = calculate_similarity(task_description, code_description)
    return resume_fit_score, code_fit_score

def index_candidate(final_analysis, candidate_id=None):
    if not candidate_id:
        candidate_id = str(uuid4())
    
    summary = final_analysis.get("summary", "")
    embedding_vector = EMBEDDING_MODEL.encode(summary).tolist()
    
    point = PointStruct(
        id=candidate_id,
        vector=embedding_vector,
        payload=final_analysis
    )
    
    qdrant_client.upsert(
        collection_name=COLLECTION,
        points=[point],
        wait=True
    )
    
    return candidate_id

def search_candidates(jd_text, limit=5):
    query_vector = EMBEDDING_MODEL.encode(jd_text).tolist()
    results = qdrant_client.search(
        collection_name=COLLECTION,
        query_vector=query_vector,
        limit=limit,
        with_payload=True
    )
    return [hit.payload for hit in results]

class QdrantScorer:
    """Handles Qdrant vector scoring for resume fit and code fit"""

    def __init__(self):
        # In-memory client (switch to host/port for production)
        self.client = QdrantClient(":memory:")
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

        # Initialize collections
        self._init_collections()

    def _init_collections(self):
        """Initialize Qdrant collections"""
        try:
            self.client.create_collection(
                collection_name="resume_fit",
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )
        except:
            pass  # Collection already exists

        try:
            self.client.create_collection(
                collection_name="code_fit",
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )
        except:
            pass

    def score_resume_fit(
        self, resume_text, ideal_candidate_profile, candidate_id
    ):
        """
        Score how well candidate resume matches ideal profile
        Returns: 1-100 score
        """
        try:
            # Embed resume and ideal profile
            resume_embedding = self.embedding_model.encode(resume_text).tolist()
            ideal_embedding = self.embedding_model.encode(
                ideal_candidate_profile
            ).tolist()

            # Store resume vector
            point_id = int(uuid.uuid4().int % (2**63))
            self.client.upsert(
                collection_name="resume_fit",
                points=[
                    PointStruct(
                        id=point_id,
                        vector=resume_embedding,
                        payload={
                            "candidate_id": candidate_id,
                            "type": "resume",
                            "text": resume_text[:500],
                        },
                    )
                ],
            )

            # Search against ideal profile
            results = self.client.search(
                collection_name="resume_fit", query_vector=ideal_embedding, limit=1
            )

            # Convert similarity score (0-1) to 1-100
            if results:
                similarity = results[0].score  # Cosine similarity: -1 to 1
                score = max(1, min(100, int((similarity + 1) / 2 * 100)))
            else:
                score = 50

            print(
                f"   Resume Fit: {score}/100 (similarity: {similarity if results else 'N/A'})"
            )
            return score

        except Exception as e:
            print(f"⚠️  Resume fit scoring error: {str(e)}")
            return 50

    def score_code_fit(self, code_description, task_description, candidate_id):
        """
        Score how well submitted code matches the task
        Returns: 1-100 score
        """
        try:
            # Embed code and task
            code_embedding = self.embedding_model.encode(code_description).tolist()
            task_embedding = self.embedding_model.encode(task_description).tolist()

            # Store code vector
            point_id = int(uuid.uuid4().int % (2**63))
            self.client.upsert(
                collection_name="code_fit",
                points=[
                    PointStruct(
                        id=point_id,
                        vector=code_embedding,
                        payload={
                            "candidate_id": candidate_id,
                            "type": "code",
                            "text": code_description[:500],
                        },
                    )
                ],
            )

            # Search against task
            results = self.client.search(
                collection_name="code_fit", query_vector=task_embedding, limit=1
            )

            # Convert similarity score to 1-100
            if results:
                similarity = results[0].score
                score = max(1, min(100, int((similarity + 1) / 2 * 100)))
            else:
                score = 50

            print(
                f"   Code Fit: {score}/100 (similarity: {similarity if results else 'N/A'})"
            )
            return score

        except Exception as e:
            print(f"⚠️  Code fit scoring error: {str(e)}")
            return 50