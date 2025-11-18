# AI Candidate Evaluation System
**Gemini + Qdrant Powered Evaluation Pipeline**

## 🔄 Evaluation Flow

```
1. Company submits task description
   ↓
2. Candidate uploads resume + task solution
   ↓
3. STAGE 1: Gemini evaluates code
   - Code quality score
   - Code description (what it achieves)
   - Generates video interview questions
   - Generates MCQ questions
   ↓
4. STAGE 2: Qdrant vector scoring
   - Resume fit score (resume vs ideal candidate)
   - Code fit score (task vs code description)
   ↓
5. Candidate takes AI video interview
   - AI character reads questions
   - Responses transcribed by Gemini
   - MCQ assessment with camera on
   ↓
6. STAGE 3: Assessment scoring
   - MCQ answers scored deterministically
   - Interview transcripts stored
   ↓
7. STAGE 4: Gemini final analysis
   - Evaluates interview transcripts
   - Calculates weighted overall score
   - Generates comprehensive feedback
   ↓
8. Candidate indexed in Qdrant
```

## 📊 Scoring Breakdown

**Overall Score = Weighted Average:**
- 15% × Resume Fit Score
- 15% × Code Fit Score
- 30% × Code Quality Score
- 25% × Video Interview Score
- 15% × MCQ Score

## 🏗️ Architecture

### Components
1. **Gemini AI**
   - Code evaluation
   - Question generation
   - Video transcription
   - Final comprehensive analysis

2. **Qdrant Vector DB**
   - Semantic similarity scoring
   - Candidate indexing
   - Search functionality

### File Structure
```
app/
├── pipeline.py              # Main evaluation pipeline
├── api.py                   # FastAPI routes
├── gemini_evaluator.py      # Gemini integration
├── qdrant_scorer.py         # Qdrant integration
├── mcq_scorer.py            # MCQ scoring logic
└── video_interview.py       # Video processing
app.py                       # FastAPI application
test.py                      # Complete test script
```

## 🚀 Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Run Server
```bash
python app.py
```

Server runs on `http://localhost:8000`

## 📡 API Endpoints

### Start Evaluation
**POST** `/api/evaluate/start`

**Form Data:**
- `resume` (file): PDF resume
- `code_solution` (text): Candidate's code
- `job_description` (text): JD text
- `ideal_candidate_profile` (text): Ideal candidate description
- `task_description` (text): Task requirements
- `candidate_id` (text): Unique identifier
- `jd_id` (text): Job identifier

**Response:**
```json
{
  "status": "success",
  "candidate_id": "john_doe_001",
  "stage": "ready_for_interview",
  "interview_questions": [...],
  "interview_audio": [...],
  "mcq_questions": [...],
  "scores_so_far": {
    "code_quality": 85,
    "resume_fit": 78,
    "code_fit": 82
  }
}
```

### Complete Evaluation
**POST** `/api/evaluate/complete`

**Form Data:**
- `candidate_id` (text)
- `interview_videos` (files): Video responses
- `mcq_answers` (text): JSON array `["A","B","C","D","A"]`

**Response:**
```json
{
  "status": "success",
  "candidate_id": "john_doe_001",
  "final_recommendation": "Strong Hire",
  "final_score": 87,
  "evaluation": {...}
}
```

### Full Evaluation (Testing)
**POST** `/api/evaluate/full`

Combines start + complete in one call.

### Get Status
**GET** `/api/evaluate/status/{candidate_id}`

## 🧪 Testing

Run complete test with mock data:
```bash
python test.py
```

This will:
1. Execute all 4 stages
2. Generate evaluation report
3. Save to `evaluation_{candidate_id}.json`

## 📝 Stage Details

### Stage 1: Gemini Code Evaluation
- Analyzes code functionality
- Scores code quality (1-100)
- Generates code description
- Creates 5-7 interview questions
- Creates 5 MCQ questions

### Stage 2: Qdrant Vector Scoring
- Embeds ideal candidate profile + resume
- Calculates cosine similarity → Resume Fit Score
- Embeds task description + code description
- Calculates cosine similarity → Code Fit Score

### Stage 3: Interview + MCQ
- Transcribes video responses via Gemini
- Scores MCQ answers deterministically
- Stores all responses

### Stage 4: Final Analysis
- Evaluates interview transcript quality
- Calculates video interview score
- Computes weighted overall score
- Generates:
  - Comprehensive summary
  - 4-6 strengths
  - 3-5 weaknesses
  - Final recommendation

## 🎯 Recommendations

| Score | Recommendation |
|-------|---------------|
| 90-100 | Strong Hire |
| 75-89 | Hire |
| 60-74 | Maybe |
| <60 | No Hire |

## 🔒 Environment Variables

```bash
GENAI_API_KEY=          # Your Gemini API key
QDRANT_URL=             # Qdrant instance URL
QDRANT_API_KEY=         # Qdrant API key
```

## 📦 Dependencies

- **FastAPI**: Web framework
- **Gemini**: AI evaluation & transcription
- **Qdrant**: Vector similarity search
- **SentenceTransformers**: Text embeddings
- **PyPDF2**: PDF processing

## 🛠️ Production Considerations

1. **Session Storage**: Replace in-memory dict with Redis
2. **Video Storage**: Use S3 or cloud storage
3. **Rate Limiting**: Add rate limits to endpoints
4. **Authentication**: Implement JWT or OAuth
5. **Logging**: Add structured logging
6. **Monitoring**: Set up health checks and metrics
7. **Error Handling**: Enhance error responses

## 📊 Example Output

```json
{
  "overall_score": 87,
  "recommendation": "Strong Hire",
  "resume_fit_score": 78,
  "code_fit_score": 82,
  "code_quality_score": 85,
  "video_interview_score": 92,
  "mcq_score": 80,
  "strengths": [
    "Strong Python expertise with 7+ years experience",
    "Excellent microservices architecture knowledge",
    "Clear communication in interview responses",
    "Production-ready code with proper error handling"
  ],
  "weaknesses": [
    "Could improve testing coverage",
    "Limited discussion of scalability considerations",
    "Some MCQ questions on advanced topics missed"
  ],
  "summary": "John is a strong candidate with extensive Python backend experience..."
}
```

## 🤝 Support

For issues or questions, please check the API documentation at `http://localhost:8000/docs` when the server is running.