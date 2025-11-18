import os
import tempfile
import subprocess
import json
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from PyPDF2 import PdfReader
from typing import List
from pydantic import BaseModel

from app.gemini_evaluator import stage1_evaluate_code
from app.pipeline import CandidateEvaluationPipeline
from app.video_interview import conduct_video_interview, generate_interview_audio

app_router = APIRouter()

# ============ PYDANTIC MODELS ============
class EvaluateStartRequest(BaseModel):
    repo_link: str
    job_description: str
    ideal_candidate_profile: str
    task_description: str
    candidate_id: str
    jd_id: str
    resume_content: str

class SubmitMCQRequest(BaseModel):
    candidate_id: str
    mcq_answers: List[str]  # ['A', 'B', 'C']

# In-memory session storage
session_storage = {}

# ============ HELPER FUNCTIONS ============
def clone_and_extract_code(repo_link: str) -> str:
    """Clone repo and extract code files (max 8KB for free tier)"""
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            subprocess.run(
                ["git", "clone", repo_link, tmpdir],
                check=True,
                capture_output=True,
                timeout=30
            )
            
            code_content = ""
            max_size = 8000
            
            for root, dirs, files in os.walk(tmpdir):
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', '.git']]
                
                for file in files:
                    if file.endswith(('.py', '.js', '.java', '.cpp', '.c', '.go', '.rs', '.ts', '.tsx')):
                        filepath = os.path.join(root, file)
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                file_content = f.read()
                                if len(code_content) + len(file_content) < max_size:
                                    code_content += f"# File: {file}\n{file_content}\n\n"
                        except:
                            pass
            
            return code_content if code_content else "No code files found in repository"
    except subprocess.TimeoutExpired:
        raise ValueError("Repository clone timed out (max 30s)")
    except subprocess.CalledProcessError:
        raise ValueError(f"Invalid repository link: {repo_link}")
    except Exception as e:
        raise ValueError(f"Failed to clone repository: {str(e)}")

# ============ ENDPOINTS ============

@app_router.post("/evaluate/start")
async def start_evaluation(request: EvaluateStartRequest):
    """
    STAGE 1 & 2: Code evaluation + vector scoring
    Returns: interview questions, MCQ questions, code description
    """
    try:
        print(f"\n📝 Starting evaluation for candidate {request.candidate_id}")
        
        # Extract code from GitHub
        print(f"🔍 Cloning repository: {request.repo_link}")
        code_solution = clone_and_extract_code(request.repo_link)
        
        # Initialize pipeline
        pipeline = CandidateEvaluationPipeline(
            jd_text=request.job_description,
            ideal_candidate_profile=request.ideal_candidate_profile,
            task_description=request.task_description,
            candidate_id=request.candidate_id,
            jd_id=request.jd_id
        )
        
        # STAGE 1: Gemini evaluation
        stage1_result = pipeline.run_stage1(code_solution)
        
        # STAGE 2: Qdrant scoring
        stage2_result = pipeline.run_stage2(request.resume_content)
        
        # Generate audio for interview questions
        interview_questions = stage1_result['interview_questions']
        audio_data = []
        for question in interview_questions:
            audio_info = generate_interview_audio(question)
            audio_data.append(audio_info)
        
        # Store pipeline in session
        session_storage[request.candidate_id] = pipeline
        
        print(f"✅ Evaluation stage 1-2 complete for {request.candidate_id}\n")
        
        return JSONResponse({
            "status": "success",
            "candidate_id": request.candidate_id,
            "stage": "ready_for_interview",
            "code_description": stage1_result.get('code_description', ''),
            "code_quality_score": stage1_result.get('code_quality_score', 0),
            "interview_questions": interview_questions,
            "interview_audio": audio_data,
            "mcq_questions": stage1_result.get('mcq_questions', []),
            "scores_so_far": {
                "code_quality": stage1_result.get('code_quality_score', 0),
                "resume_fit": stage2_result.get('resume_fit_score', 0),
                "code_fit": stage2_result.get('code_fit_score', 0)
            }
        })
    except ValueError as e:
        print(f"❌ Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        print(f"❌ Runtime error: {str(e)}")
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Evaluation start error: {str(e)}")

@app_router.post("/evaluate/submit-responses")
async def submit_interview_responses(
    candidate_id: str = Form(...),
    interview_videos: List[UploadFile] = File(...),
    mcq_answers: str = Form(...)
):
    """
    STAGE 3 & 4: Process video + MCQ responses, generate final evaluation
    """
    try:
        if candidate_id not in session_storage:
            raise HTTPException(status_code=404, detail="Session not found")
        
        pipeline = session_storage[candidate_id]
        
        print(f"\n🎬 Processing responses for {candidate_id}")
        
        # Read video files
        video_data_list = []
        for video_file in interview_videos:
            video_bytes = await video_file.read()
            video_data_list.append(video_bytes)
        
        # Parse MCQ answers
        mcq_answers_list = json.loads(mcq_answers)
        
        # STAGE 3: Transcribe videos + score MCQ
        interview_questions = pipeline.get_interview_questions()
        interview_transcripts = conduct_video_interview(interview_questions, video_data_list)
        stage3_result = pipeline.run_stage3(interview_transcripts, mcq_answers_list)
        
        # STAGE 4: Gemini final analysis
        stage4_result = pipeline.run_stage4()
        
        # Clean up session
        del session_storage[candidate_id]
        
        print(f"✅ Evaluation complete for {candidate_id}\n")
        
        return JSONResponse({
            "status": "success",
            "candidate_id": candidate_id,
            "overall_score": stage4_result['overall_score'],
            "recommendation": stage4_result['recommendation'],
            "summary": stage4_result['summary'],
            "strengths": stage4_result['strengths'],
            "weaknesses": stage4_result['weaknesses'],
            "scores": {
                "code_quality": pipeline.stage1_result['code_quality_score'],
                "resume_fit": pipeline.stage2_result['resume_fit_score'],
                "code_fit": pipeline.stage2_result['code_fit_score'],
                "mcq": stage3_result['mcq_score'],
                "video_interview": stage4_result['video_interview_score']
            }
        })
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Evaluation error: {str(e)}")

@app_router.get("/evaluate/status/{candidate_id}")
async def get_status(candidate_id: str):
    """Check evaluation status"""
    if candidate_id in session_storage:
        return JSONResponse({
            "status": "in_progress",
            "candidate_id": candidate_id
        })
    return JSONResponse({
        "status": "not_found"
    })