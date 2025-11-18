import os
import json
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import List
from pydantic import BaseModel

from app.pipeline import CandidateEvaluationPipeline
from app.video_interview import generate_interview_audio

app_router = APIRouter()

# In-memory session storage (use Redis in production)
session_storage = {}

# ============ ENDPOINTS ============

@app_router.post("/evaluate/start")
async def start_evaluation(
    repo_link: str = Form(...),
    job_description: str = Form(...),
    ideal_candidate_profile: str = Form(...),
    task_description: str = Form(...),
    candidate_id: str = Form(...),
    jd_id: str = Form(...),
    resume_file: UploadFile = File(...)
):
    """
    STAGE 1: Initial Evaluation
    
    Flow:
    1. Receive resume PDF and GitHub repo link
    2. Gemini evaluates code from GitHub
    3. Gemini generates code description
    4. Gemini generates 5 interview questions (specific to candidate's code)
    5. Gemini generates 3 MCQ questions
    6. Qdrant calculates resume fit score (resume vs ideal profile)
    7. Qdrant calculates code fit score (code description vs task)
    8. Generate TTS audio for interview questions (optional)
    
    Returns:
    - interview_questions: List of 5 questions for video interview
    - interview_audio: Optional TTS audio for each question
    - mcq_questions: List of 3 MCQ questions
    - Initial scores: code_quality, resume_fit, code_fit
    """
    try:
        print(f"\n{'='*70}")
        print(f"🚀 STARTING EVALUATION FOR CANDIDATE: {candidate_id}")
        print(f"{'='*70}")
        print(f"📍 Job: {jd_id}")
        print(f"🔗 GitHub: {repo_link}")
        print(f"📄 Resume: {resume_file.filename}")
        
        # Validate inputs
        if not repo_link.startswith("https://github.com/"):
            raise ValueError("Invalid GitHub repository URL")
        
        if not resume_file.filename.endswith('.pdf'):
            raise ValueError("Resume must be a PDF file")
        
        # Read resume PDF
        resume_bytes = await resume_file.read()
        
        if len(resume_bytes) < 1000:  # Less than 1KB
            raise ValueError("Resume file appears to be empty or corrupted")
        
        print(f"✅ Resume loaded: {len(resume_bytes)} bytes")
        
        # Initialize pipeline
        pipeline = CandidateEvaluationPipeline(
            jd_text=job_description,
            ideal_candidate_profile=ideal_candidate_profile,
            task_description=task_description,
            candidate_id=candidate_id,
            jd_id=jd_id
        )
        
        # RUN STAGE 1: Complete initial evaluation
        stage1_results = pipeline.run_stage1(
            repo_link=repo_link,
            resume_bytes=resume_bytes
        )
        
        # Generate audio for interview questions (optional enhancement)
        print(f"\n🔊 Generating TTS audio for interview questions...")
        interview_audio = []
        for question in stage1_results['interview_questions']:
            audio_info = generate_interview_audio(question)
            interview_audio.append(audio_info)
        
        # Store pipeline in session for Stage 3
        session_storage[candidate_id] = pipeline
        
        print(f"\n{'='*70}")
        print(f"✅ STAGE 1 COMPLETE - Ready for Interview")
        print(f"{'='*70}\n")
        
        return JSONResponse({
            "status": "success",
            "message": "Initial evaluation complete. Candidate can now proceed to video interview.",
            "candidate_id": candidate_id,
            "jd_id": jd_id,
            "stage": "ready_for_interview",
            
            # Code evaluation results
            "code_quality_score": stage1_results['code_quality_score'],
            "code_description": stage1_results['code_description'],
            
            # Interview questions (5 questions specific to their code)
            "interview_questions": stage1_results['interview_questions'],
            "interview_audio": interview_audio,
            
            # MCQ questions (3 questions)
            "mcq_questions": stage1_results['mcq_questions'],
            
            # Initial scores
            "scores_so_far": {
                "code_quality": stage1_results['code_quality_score'],
                "resume_fit": stage1_results['resume_fit_score'],
                "code_fit": stage1_results['code_fit_score']
            },
            
            # Instructions for next step
            "next_step": "Candidate should record video responses to interview_questions and answer mcq_questions"
        })
        
    except ValueError as e:
        print(f"❌ Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except RuntimeError as e:
        print(f"❌ Runtime error: {str(e)}")
        raise HTTPException(status_code=503, detail=str(e))
    
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Evaluation start error: {str(e)}")


@app_router.post("/evaluate/submit-responses")
async def submit_interview_responses(
    candidate_id: str = Form(...),
    interview_videos: List[UploadFile] = File(...),
    mcq_answers: str = Form(...)  # JSON string: ["A", "B", "C"]
):
    """
    STAGE 3: Process Responses and Final Evaluation
    
    Flow:
    1. Receive video responses and MCQ answers
    2. Gemini transcribes all video responses (speech to text)
    3. Score MCQ answers deterministically
    4. Gemini performs final comprehensive analysis:
       - Analyzes resume PDF again
       - Analyzes code from GitHub again
       - Evaluates interview transcripts
       - Calculates video_interview_score
       - Calculates weighted overall_score
       - Generates summary, strengths, weaknesses, recommendation
    
    Returns:
    - overall_score: Weighted final score (1-100)
    - video_interview_score: Score for interview performance
    - All individual scores
    - recommendation: "Strong Hire", "Hire", "Maybe", or "No Hire"
    - summary: Professional summary
    - strengths: List of strengths
    - weaknesses: List of areas for improvement
    """
    try:
        print(f"\n{'='*70}")
        print(f"🎬 PROCESSING RESPONSES FOR CANDIDATE: {candidate_id}")
        print(f"{'='*70}")
        
        # Retrieve pipeline from session
        if candidate_id not in session_storage:
            raise HTTPException(
                status_code=404,
                detail="Session not found. Please restart the evaluation from /evaluate/start"
            )
        
        pipeline = session_storage[candidate_id]
        
        # Validate inputs
        if not interview_videos or len(interview_videos) == 0:
            raise ValueError("No interview videos provided")
        
        print(f"📹 Received {len(interview_videos)} video files")
        
        # Read all video files
        video_data_list = []
        for i, video_file in enumerate(interview_videos):
            video_bytes = await video_file.read()
            
            if len(video_bytes) < 1000:  # Less than 1KB
                print(f"   ⚠️ Warning: Video {i+1} appears to be empty or very small")
            
            video_data_list.append(video_bytes)
            print(f"   ✅ Video {i+1}: {len(video_bytes)} bytes")
        
        # Parse MCQ answers
        try:
            mcq_answers_list = json.loads(mcq_answers)
            print(f"📝 Received {len(mcq_answers_list)} MCQ answers: {mcq_answers_list}")
        except json.JSONDecodeError:
            raise ValueError("Invalid MCQ answers format. Expected JSON array like [\"A\", \"B\", \"C\"]")
        
        # RUN STAGE 3: Transcribe, score, and analyze
        final_results = pipeline.run_stage3(
            interview_videos=video_data_list,
            mcq_answers=mcq_answers_list
        )
        
        # Clean up session
        del session_storage[candidate_id]
        
        print(f"\n{'='*70}")
        print(f"✅ EVALUATION COMPLETE")
        print(f"   Overall Score: {final_results['overall_score']}/100")
        print(f"   Recommendation: {final_results['recommendation']}")
        print(f"{'='*70}\n")
        
        return JSONResponse({
            "status": "success",
            "message": "Evaluation complete!",
            "candidate_id": candidate_id,
            
            # Final scores
            "overall_score": final_results['overall_score'],
            "recommendation": final_results['recommendation'],
            
            # Detailed breakdown
            "scores": final_results['scores'],
            
            # Comprehensive feedback
            "summary": final_results['summary'],
            "strengths": final_results['strengths'],
            "weaknesses": final_results['weaknesses'],
            
            # Metadata
            "evaluation_complete": True
        })
        
    except ValueError as e:
        print(f"❌ Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        print(f"❌ Error processing responses: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Response processing error: {str(e)}")


@app_router.get("/evaluate/status/{candidate_id}")
async def get_evaluation_status(candidate_id: str):
    """
    Check if evaluation is in progress
    """
    if candidate_id in session_storage:
        pipeline = session_storage[candidate_id]
        return JSONResponse({
            "status": "in_progress",
            "candidate_id": candidate_id,
            "jd_id": pipeline.jd_id,
            "stage": "awaiting_interview_responses"
        })
    
    return JSONResponse({
        "status": "not_found",
        "message": "No active evaluation found for this candidate"
    })


@app_router.delete("/evaluate/cancel/{candidate_id}")
async def cancel_evaluation(candidate_id: str):
    """
    Cancel an in-progress evaluation
    """
    if candidate_id in session_storage:
        del session_storage[candidate_id]
        return JSONResponse({
            "status": "success",
            "message": "Evaluation cancelled"
        })
    
    return JSONResponse({
        "status": "not_found",
        "message": "No active evaluation to cancel"
    })


@app_router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return JSONResponse({
        "status": "healthy",
        "active_evaluations": len(session_storage)
    })