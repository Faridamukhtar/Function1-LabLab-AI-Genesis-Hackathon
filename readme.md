# 🚀 AI Micro-Apprenticeship Platform

An intelligent hiring platform that evaluates candidates through **AI-powered code analysis**, **personalized video interviews**, and **comprehensive scoring**.

## 🎯 What Makes This Special

1. **Real GitHub Code Analysis**: Fetches and evaluates actual code from candidate repositories
2. **Dynamic Interview Questions**: Gemini generates questions specific to each candidate's code
3. **AI Video Transcription**: Multimodal AI transcribes and evaluates video responses
4. **Vector Similarity Scoring**: Uses Qdrant for semantic matching of resumes and code
5. **Comprehensive Evaluation**: Weighted scoring across 5 dimensions

---

## 🔄 Complete Evaluation Flow

### **STAGE 1: Initial Evaluation** (`POST /api/evaluate/start`)

**Input:**
- Resume PDF
- GitHub repository link
- Job description
- Ideal candidate profile
- Task description

**Process:**
1. **Gemini fetches code from GitHub** (via GitHub API)
2. **Gemini evaluates code quality** (functionality, structure, best practices)
3. **Gemini generates code description** (what the code achieves)
4. **Gemini creates 5 interview questions** (specific to their code implementation)
5. **Gemini creates 3 MCQ questions** (testing technical understanding)
6. **Qdrant calculates resume fit score** (resume text vs ideal candidate profile)
7. **Qdrant calculates code fit score** (code description vs task requirements)
8. **Optional: Generate TTS audio** for interview questions

**Output:**
```json
{
  "interview_questions": [
    "I noticed you used a hash map in your solution. Can you explain why you chose this data structure?",
    "How would you handle the case where the input array is empty?",
    ...
  ],
  "mcq_questions": [
    {
      "question": "What is the time complexity of your solution?",
      "options": ["O(n)", "O(n log n)", "O(n²)", "O(1)"],
      "correct_answer": "A"
    },
    ...
  ],
  "scores_so_far": {
    "code_quality": 85,
    "resume_fit": 78,
    "code_fit": 82
  }
}
```

---

### **STAGE 2: Candidate Interview** (Frontend)

**Process:**
1. Display interview questions one by one
2. Candidate records video response to each question
3. Display MCQ questions
4. Candidate selects answers

**Frontend Requirements:**
- Camera/microphone access
- Video recording (WebM format recommended)
- Video upload (up to 50MB per file)

---

### **STAGE 3: Final Evaluation** (`POST /api/evaluate/submit-responses`)

**Input:**
- Video responses (one per interview question)
- MCQ answers (["A", "B", "C"])

**Process:**
1. **Gemini transcribes all video responses** (multimodal speech-to-text)
2. **Score MCQ answers** deterministically against correct answers
3. **Gemini performs comprehensive analysis**:
   - Re-analyzes resume PDF
   - Re-analyzes GitHub code
   - Evaluates interview transcripts
   - Calculates video_interview_score
   - Calculates weighted overall_score
   - Generates summary, strengths, weaknesses, recommendation

**Scoring Weights:**
- **30%** Code Quality (implementation, best practices)
- **25%** Video Interview (communication, technical depth)
- **15%** Resume Fit (match with ideal profile)
- **15%** Code Fit (solution addresses task)
- **15%** MCQ Score (technical knowledge)

**Output:**
```json
{
  "overall_score": 82,
  "recommendation": "Hire",
  "scores": {
    "code_quality": 85,
    "resume_fit": 78,
    "code_fit": 82,
    "mcq": 67,
    "video_interview": 88
  },
  "summary": "Strong technical candidate with excellent problem-solving skills...",
  "strengths": [
    "Clean, well-structured code with proper error handling",
    "Articulate communication during interview",
    "Deep understanding of algorithm complexity"
  ],
  "weaknesses": [
    "Could improve documentation",
    "Some edge cases not fully handled"
  ]
}
```

---

## 📦 Installation & Setup

### Prerequisites
- Python 3.10+
- Node.js 18+ (for frontend)
- Google Gemini API key
- (Optional) Qdrant Cloud account
- (Optional) GitHub Personal Access Token

### Backend Setup

```bash
# Clone repository
git clone <your-repo>
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.template .env
# Edit .env and add your API keys

# Run server
python main.py
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

---

## 🔑 API Endpoints

### 1. Start Evaluation

```http
POST /api/evaluate/start
Content-Type: multipart/form-data

{
  "repo_link": "https://github.com/username/repo",
  "resume_file": <PDF file>,
  "job_description": "...",
  "ideal_candidate_profile": "...",
  "task_description": "...",
  "candidate_id": "CAND_12345",
  "jd_id": "JD_001"
}
```

### 2. Submit Responses

```http
POST /api/evaluate/submit-responses
Content-Type: multipart/form-data

{
  "candidate_id": "CAND_12345",
  "interview_videos": [<video1.webm>, <video2.webm>, ...],
  "mcq_answers": '["A", "B", "C"]'
}
```

### 3. Check Status

```http
GET /api/evaluate/status/{candidate_id}
```

### 4. Health Check

```http
GET /api/health
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    React Frontend                        │
│  (Resume Upload, Code Submission, Video Interview, MCQ) │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   FastAPI Backend                        │
│                    (main.py, api.py)                     │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼             ▼
   ┌────────┐  ┌─────────┐  ┌──────────┐
   │ Gemini │  │ Qdrant  │  │  GitHub  │
   │   AI   │  │ Vector  │  │   API    │
   │        │  │   DB    │  │          │
   └────────┘  └─────────┘  └──────────┘
      │
      ├─ Code Evaluation
      ├─ Question Generation
      ├─ Video Transcription
      ├─ Final Analysis
```

---

## 📊 Scoring Breakdown

### Code Quality Score (30%)
- Functionality and correctness
- Code structure and readability
- Error handling
- Performance considerations
- Best practices

### Video Interview Score (25%)
- Technical accuracy
- Communication clarity
- Problem-solving approach
- Depth of understanding
- Professionalism

### Resume Fit Score (15%)
- Vector similarity between resume and ideal profile
- Extracted via Gemini PDF processing
- Scored using Qdrant cosine similarity

### Code Fit Score (15%)
- Vector similarity between code description and task
- Measures how well solution addresses requirements

### MCQ Score (15%)
- Deterministic scoring
- Tests technical knowledge
- Generated based on candidate's code

---

## 🎨 Key Features

### 1. **Real GitHub Integration**
```python
# Fetches actual code files from GitHub
code_content = fetch_github_code("https://github.com/user/repo")
```

### 2. **Dynamic Question Generation**
```python
# Questions specific to candidate's code
interview_questions = stage1_evaluate_code(...)
# Example: "Why did you use a hash map instead of an array?"
```

### 3. **Multimodal Video Transcription**
```python
# Gemini processes video + audio
transcriptions = transcribe_video_responses(videos)
```

### 4. **Vector Semantic Matching**
```python
# Qdrant calculates similarity scores
resume_fit = qdrant_scorer.score_resume_fit(resume_pdf, ideal_profile)
code_fit = qdrant_scorer.score_code_fit(code_desc, task_desc)
```

---

## 🚨 Important Notes

### GitHub Code Fetching
- Requires valid GitHub URL
- Supports public repositories
- For private repos: Add `GITHUB_TOKEN` to `.env`
- Fetches up to 10 most relevant code files

### Video Requirements
- Format: WebM (recommended) or MP4
- Max size: 50MB per video
- Must include audio for transcription
- Number of videos must match number of questions

### PDF Resume
- Must be valid PDF format
- Text must be extractable (not scanned images)
- Max size: 10MB

---

## 🐛 Troubleshooting

### "GitHub fetch failed"
- Check repository URL is valid and public
- Add `GITHUB_TOKEN` for private repos or higher rate limits

### "Resume extraction failed"
- Ensure PDF is text-based, not scanned image
- Try a different PDF generator

### "Video transcription failed"
- Check video has audio track
- Ensure video isn't corrupted
- Verify video format is WebM or MP4

### "Session not found"
- Complete Stage 1 before Stage 3
- Check `candidate_id` matches between requests

---

## 📝 Example Usage

```python
# Backend Test Script
import requests

# Stage 1: Start evaluation
with open('resume.pdf', 'rb') as f:
    response = requests.post('http://localhost:8000/api/evaluate/start', files={
        'resume_file': f
    }, data={
        'repo_link': 'https://github.com/user/solution',
        'candidate_id': 'CAND_001',
        'jd_id': 'JD_001',
        'job_description': '...',
        'ideal_candidate_profile': '...',
        'task_description': '...'
    })

data = response.json()
print(f"Interview Questions: {data['interview_questions']}")

# Stage 3: Submit responses
with open('video1.webm', 'rb') as v1, open('video2.webm', 'rb') as v2:
    response = requests.post('http://localhost:8000/api/evaluate/submit-responses', files={
        'interview_videos': [v1, v2, ...]
    }, data={
        'candidate_id': 'CAND_001',
        'mcq_answers': '["A", "B", "C"]'
    })

result = response.json()
print(f"Overall Score: {result['overall_score']}")
print(f"Recommendation: {result['recommendation']}")
```

---

## 🏆 Winning Strategy for AI Genesis Hackathon

### Innovation Highlights
1. **Real GitHub Code Fetching** - Not just analyzing uploaded files
2. **Dynamic Personalized Questions** - Each candidate gets unique interview
3. **Multimodal AI** - Video + Audio + PDF + Code analysis
4. **Semantic Matching** - Vector similarity for intelligent scoring
5. **Production-Ready** - Complete pipeline with error handling

### Demo Flow
1. Show landing page with role selection
2. Candidate applies with resume + GitHub repo
3. AI generates custom questions in real-time
4. Candidate records video interview
5. Comprehensive evaluation with detailed breakdown
6. Company dashboard (future) to search candidates

---

## 📄 License

MIT License - Built for AI Genesis Hackathon 2025

---

## 🤝 Contributing

This is a hackathon project, but contributions are welcome!

---

**Built with ❤️ using Gemini, Qdrant, FastAPI, and React**