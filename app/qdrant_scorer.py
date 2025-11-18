import os
import numpy as np
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, Distance, VectorParams
from uuid import uuid4

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