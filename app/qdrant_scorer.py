import os
import uuid
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import google.generativeai as genai

load_dotenv()

# ------------------------------------------
# GEMINI CONFIG (FREE TIER)
# ------------------------------------------
GENAI_API_KEY = os.getenv("GENAI_API_KEY")
genai.configure(api_key=GENAI_API_KEY)

PDF_MODEL = genai.GenerativeModel("gemini-flash-latest")


# ------------------------------------------
# EMBEDDINGS
# ------------------------------------------
EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
VECTOR_DIM = EMBEDDING_MODEL.get_sentence_embedding_dimension()


# ------------------------------------------
# OPTIONAL: QDRANT (for SEARCH, NOT SCORING)
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
else:
    print("⚠️ Qdrant cloud not configured - running without persistent storage")
    qdrant_client = None


# ------------------------------------------
# PDF TEXT EXTRACTION
# ------------------------------------------
def extract_resume_text_from_pdf(resume_bytes: bytes) -> str:
    print(f"   📄 Extracting text from PDF resume...")

    try:
        response = PDF_MODEL.generate_content(
            [
                {"mime_type": "application/pdf", "data": resume_bytes},
                """
                Extract all text from this PDF. Return only raw text.
                Maintain order. No comments. No analysis.
                """
            ],
            generation_config={
                "temperature": 0.1,
                "max_output_tokens": 3000
            }
        )

        text = response.text.strip()

        if not text or len(text) < 50:
            print("   ⚠️ Resume extraction too short")
            return "Resume content could not be extracted properly"

        print(f"   ✅ Extracted {len(text)} characters")
        return text

    except Exception as e:
        print(f"   ❌ Gemini PDF error: {str(e)}")
        return "Resume content could not be extracted"


# ------------------------------------------
# OPTIONAL: INDEX CANDIDATE IN QDRANT
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
# OPTIONAL: SEARCH CANDIDATES
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
# 🚀 FIXED SCORER — NO MORE QDRANT MISSCORING
# ==========================================================
class QdrantScorer:
    """
    Balanced Scorer:
    - Gemini semantic relevance (60%)
    - Qdrant embedding alignment (20%)
    - Irrelevance Penalization (20%)
    """

    def __init__(self):
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

    # ------------------------------------------------------
    # Resume extraction through Gemini
    # ------------------------------------------------------
    def _extract_resume_text(self, resume_bytes):
        try:
            resp = PDF_MODEL.generate_content(
                [
                    {"mime_type": "application/pdf", "data": resume_bytes},
                    "Extract all technical and experience-related content."
                ],
                generation_config={"temperature": 0.1}
            )
            return resp.text.strip()
        except:
            return ""

    # ------------------------------------------------------
    # Gemini semantic relevance (0–100)
    # ------------------------------------------------------
    def _gemini_relevance_score(self, jd, resume_text):
        prompt = f"""
Evaluate how well this resume matches this job description.

JOB DESCRIPTION:
{jd}

RESUME:
{resume_text}

Criteria:
- React experience
- JavaScript, HTML, CSS
- UI/Frontend development
- Project relevance to frontend
- Experience depth and recency

Return a number from 1 to 100 only.
"""
        try:
            resp = PDF_MODEL.generate_content(
                prompt, generation_config={"temperature": 0.0, "max_output_tokens": 20}
            )
            num = ''.join(c for c in resp.text if c.isdigit())
            return max(1, min(100, int(num))) if num else 50
        except:
            return 50

    # ------------------------------------------------------
    # Qdrant vector alignment score (0–100)
    # ------------------------------------------------------
    def _embedding_alignment(self, jd, resume_text):
        try:
            jd_vec = self.embedding_model.encode(jd)
            cv_vec = self.embedding_model.encode(resume_text)
            sim = float(cos_sim(jd_vec, cv_vec))  # -1..1
            score = int(((sim + 1) / 2) * 100)
            return max(1, min(100, score))
        except:
            return 40

    # ------------------------------------------------------
    # PENALIZATION SCORE (0–100)
    # ------------------------------------------------------
    def _penalty_score(self, jd, resume_text):
        resume_lower = resume_text.lower()
        jd_lower = jd.lower()

        penalties = 0

        # Missing core keywords
        must_have = ["react", "javascript", "html", "css", "frontend", "ui"]
        for kw in must_have:
            if kw in jd_lower and kw not in resume_lower:
                penalties += 8     # soft penalty

        # Too short
        if len(resume_text) < 200:
            penalties += 15

        # Generic filler / no projects
        if "project" not in resume_lower:
            penalties += 10

        # Penalty cannot exceed 70 (to avoid overkill)
        penalties = min(penalties, 70)

        # Convert to penalty score 0–100 (higher = better)
        penalty_score = 100 - penalties
        return max(10, penalty_score)

    # ------------------------------------------------------
    # FINAL SCORE (balanced)
    # ------------------------------------------------------
    def score_resume_fit(self, resume_bytes, ideal_candidate_profile, candidate_id=None):
        print("\n   📊 Balanced Resume Scoring (Gemini + Qdrant + penalties)…")

        resume_text = self._extract_resume_text(resume_bytes)
        if not resume_text:
            print("   ❌ No text extracted → default 35")
            return 35

        # Components
        relevance = self._gemini_relevance_score(ideal_candidate_profile, resume_text)
        embedding = self._embedding_alignment(ideal_candidate_profile, resume_text)
        penalty = self._penalty_score(ideal_candidate_profile, resume_text)

        # Final weighted score
        final = int(
            (relevance * 0.6) +
            (embedding * 0.2) +
            (penalty * 0.2)
        )

        final = max(1, min(100, final))

        print(f"      Gemini relevance: {relevance}")
        print(f"      Vector alignment: {embedding}")
        print(f"      Penalty score:    {penalty}")
        print(f"   ✅ Final Resume Score → {final}/100")

        return final
