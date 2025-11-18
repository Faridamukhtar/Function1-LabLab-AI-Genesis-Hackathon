import os
import uuid
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

load_dotenv()

# ------------------------------------------
# EMBEDDINGS
# ------------------------------------------
EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
VECTOR_DIM = EMBEDDING_MODEL.get_sentence_embedding_dimension()


# ------------------------------------------
# QDRANT SETUP
# ------------------------------------------
qdrant_url = os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_API_KEY")

if qdrant_url and qdrant_api_key:
    qdrant_client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
    COLLECTION = "candidates"

    if not qdrant_client.collection_exists(COLLECTION):
        qdrant_client.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=VECTOR_DIM, distance=Distance.COSINE)
        )
    
    # Create code_fit collection if it doesn't exist
    if not qdrant_client.collection_exists("code_fit"):
        qdrant_client.create_collection(
            collection_name="code_fit",
            vectors_config=VectorParams(size=VECTOR_DIM, distance=Distance.COSINE)
        )
else:
    print("⚠️ Qdrant cloud not configured - running without persistent storage")
    qdrant_client = None


# ------------------------------------------
# PDF TEXT EXTRACTION (Simple)
# ------------------------------------------
def extract_resume_text_from_pdf(resume_bytes: bytes) -> str:
    """
    Extract text from PDF using PyPDF2 or pdfplumber
    Install: pip install PyPDF2
    """
    print(f"   📄 Extracting text from PDF resume...")
    
    try:
        import io
        from PyPDF2 import PdfReader
        
        pdf_file = io.BytesIO(resume_bytes)
        reader = PdfReader(pdf_file)
        
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        
        text = text.strip()
        
        if not text or len(text) < 50:
            print("   ⚠️ Resume extraction too short")
            return "Resume content could not be extracted properly"
        
        print(f"   ✅ Extracted {len(text)} characters")
        return text
        
    except Exception as e:
        print(f"   ❌ PDF extraction error: {str(e)}")
        return "Resume content could not be extracted"


# ------------------------------------------
# INDEX CANDIDATE IN QDRANT
# ------------------------------------------
def index_candidate(final_analysis: dict, candidate_id: str = None):
    if not qdrant_client:
        return candidate_id or str(uuid.uuid4())

    candidate_id = candidate_id or str(uuid.uuid4())

    try:
        summary = final_analysis.get("summary", "")
        embedding = EMBEDDING_MODEL.encode(summary).tolist()

        qdrant_client.upsert(
            collection_name=COLLECTION,
            points=[PointStruct(id=candidate_id, vector=embedding, payload=final_analysis)],
            wait=True
        )

        print(f"   ✅ Indexed candidate {candidate_id}")
        return candidate_id

    except Exception as e:
        print(f"   ⚠️ Indexing failed: {str(e)}")
        return candidate_id


# ------------------------------------------
# SEARCH CANDIDATES
# ------------------------------------------
def search_candidates(jd_text: str, limit: int = 5):
    if not qdrant_client:
        return []

    try:
        query_vector = EMBEDDING_MODEL.encode(jd_text).tolist()
        results = qdrant_client.search(
            collection_name=COLLECTION,
            query_vector=query_vector,
            limit=limit,
            with_payload=True
        )
        return [hit.payload for hit in results]
    except Exception as e:
        print(f"   ⚠️ Search failed: {str(e)}")
        return []


# ==========================================================
# 🚀 EMBEDDING-BASED SCORER (NO GEMINI)
# ==========================================================
class QdrantScorer:
    """
    Pure embedding-based scoring using semantic similarity
    - Uses sentence transformers for all scoring
    - No external API calls needed
    """

    def __init__(self):
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.client = qdrant_client

    # ------------------------------------------------------
    # Resume extraction (simple PDF parsing)
    # ------------------------------------------------------
    def _extract_resume_text(self, resume_bytes):
        try:
            import io
            from PyPDF2 import PdfReader
            
            pdf_file = io.BytesIO(resume_bytes)
            reader = PdfReader(pdf_file)
            
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            text = text.strip()
            print(f"   📄 Extracted {len(text)} characters from resume")
            return text
        except Exception as e:
            print(f"   ❌ Extraction error: {str(e)}")
            return ""

    # ------------------------------------------------------
    # Semantic similarity score (0-100)
    # ------------------------------------------------------
    def _semantic_similarity_score(self, text1, text2):
        """
        Calculate semantic similarity between two texts
        Returns score from 1-100
        """
        try:
            vec1 = self.embedding_model.encode(text1)
            vec2 = self.embedding_model.encode(text2)
            sim = float(cos_sim(vec1, vec2))  # -1 to 1
            score = int(((sim + 1) / 2) * 100)  # Convert to 1-100
            return max(1, min(100, score))
        except Exception as e:
            print(f"   ⚠️ Similarity calculation error: {str(e)}")
            return 50

    # ------------------------------------------------------
    # Key skills matching score (0-100)
    # ------------------------------------------------------
    def _skills_match_score(self, jd, resume_text):
        """
        Extract and compare key technical terms
        """
        try:
            # Simple keyword extraction (can be enhanced)
            jd_lower = jd.lower()
            resume_lower = resume_text.lower()
            
            # Common tech keywords
            keywords = [
                'python', 'java', 'javascript', 'react', 'node', 'aws', 'docker',
                'kubernetes', 'sql', 'nosql', 'api', 'machine learning', 'ai',
                'data', 'cloud', 'agile', 'git', 'ci/cd', 'testing'
            ]
            
            matches = sum(1 for kw in keywords if kw in jd_lower and kw in resume_lower)
            jd_keywords = sum(1 for kw in keywords if kw in jd_lower)
            
            if jd_keywords == 0:
                return 50
            
            score = int((matches / jd_keywords) * 100)
            return max(1, min(100, score))
        except:
            return 50

    # ------------------------------------------------------
    # FINAL RESUME FIT SCORE (balanced)
    # ------------------------------------------------------
    def score_resume_fit(self, resume_bytes, ideal_candidate_profile, candidate_id=None):
        """
        Score resume against job description
        Returns: 1-100 score
        """
        print(f"   📊 Scoring resume fit...")
        
        resume_text = self._extract_resume_text(resume_bytes)
        if not resume_text:
            print("   ❌ No text extracted → default 35")
            return 35

        # Calculate components
        semantic_score = self._semantic_similarity_score(ideal_candidate_profile, resume_text)
        skills_score = self._skills_match_score(ideal_candidate_profile, resume_text)

        # Weighted final score
        # 70% semantic similarity, 30% skills match
        final = int((semantic_score * 0.7) + (skills_score * 0.3))
        final = max(1, min(100, final))

        print(f"   ✅ Semantic: {semantic_score}/100, Skills: {skills_score}/100")
        print(f"   🎯 Final Score: {final}/100")

        return final

    # ------------------------------------------------------
    # CODE FIT SCORING
    # ------------------------------------------------------
    def score_code_fit(self, code_description, task_description, candidate_id):
        """
        Score how well submitted code matches the task
        Returns: 1-100 score
        """
        if not self.client:
            print("   ⚠️ Qdrant not configured, using direct similarity")
            return self._semantic_similarity_score(code_description, task_description)
        
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
                collection_name="code_fit", 
                query_vector=task_embedding, 
                limit=1
            )

            # Convert similarity score to 1-100
            if results:
                similarity = results[0].score
                score = max(1, min(100, int((similarity + 1) / 2 * 100)))
            else:
                score = 50

            print(f"   🎯 Code Fit: {score}/100 (similarity: {similarity if results else 'N/A'})")
            return score

        except Exception as e:
            print(f"   ⚠️ Code fit scoring error: {str(e)}")
            return 50