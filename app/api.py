import os
import tempfile
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from PyPDF2 import PdfReader
from typing import List
import json

from app.pipeline import CandidateEvaluationPipeline
from app.video_interview import conduct_video_interview, generate_interview_audio

router = APIRouter()

def extract_text_from_pdf(file: UploadFile) -> str:
    """Extract text from PDF resume."""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            content = file.file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        reader = PdfReader(tmp_file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        
        os.unlink(tmp_file_path)
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not process PDF file: {e}")

# In-memory storage for sessions (use Redis in production)
session_storage = {}

@router.post("/evaluate/start")
async def start_evaluation(
    resume: UploadFile = File(..., description="Candidate's resume (PDF)"),
    code_solution: str = Form(..., description="Candidate's code solution"),
    job_description: str = Form(..., description="Job description text"),
    ideal_candidate_profile: str = Form(..., description="Ideal candidate profile"),
    task_description: str = Form(..., description="Task description for code solution"),
    candidate_id: str = Form(..., description="Unique candidate identifier"),
    jd_id: str = Form(..., description="Job description identifier")
):
    """
    STAGE 1 & 2: 
    - Upload resume + code
    - Gemini evaluates code + generates questions
    - Qdrant scores resume fit & code fit
    - Returns interview questions with AI audio
    """
    try:
        resume_text = extract_text_from_pdf(resume)
        
        pipeline = CandidateEvaluationPipeline(
            jd_text=job_description,
            ideal_candidate_profile=ideal_candidate_profile,
            task_description=task_description,
            candidate_id=candidate_id,
            jd_id=jd_id
        )
        
        # STAGE 1: Gemini code evaluation + question generation
        stage1_result = pipeline.run_stage1(code_solution)
        
        # STAGE 2: Qdrant vector scoring
        stage2_result = pipeline.run_stage2(resume_text)
        
        # Generate AI character audio for interview questions
        interview_questions = stage1_result['interview_questions']
        mcq_questions = stage1_result['mcq_questions']
        
        interview_audio_data = []
        for question in interview_questions:
            audio_info = generate_interview_audio(question, character_persona="professional_interviewer")
            interview_audio_data.append(audio_info)
        
        # Store session data for stage 3
        session_storage[candidate_id] = {
            "pipeline": pipeline
        }
        
        return JSONResponse({
            "status": "success",
            "candidate_id": candidate_id,
            "stage": "ready_for_interview",
            "interview_questions": interview_questions,
            "interview_audio": interview_audio_data,
            "mcq_questions": mcq_questions,
            "scores_so_far": {
                "code_quality": stage1_result['code_quality_score'],
                "resume_fit": stage2_result['resume_fit_score'],
                "code_fit": stage2_result['code_fit_score']
            }
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation start error: {str(e)}")

@router.post("/evaluate/complete")
async def complete_evaluation(
    candidate_id: str = Form(...),
    interview_videos: List[UploadFile] = File(..., description="Video responses from candidate"),
    mcq_answers: str = Form(..., description="JSON array of MCQ answers ['A','B','C','D','A']")
):
    """
    STAGE 3 & 4: 
    - Process video interview + MCQ
    - Gemini final analysis
    - Index in Qdrant
    """
    try:
        if candidate_id not in session_storage:
            raise HTTPException(status_code=404, detail="Session not found. Please start evaluation first.")
        
        pipeline = session_storage[candidate_id]["pipeline"]
        
        # Parse MCQ answers
        mcq_answers_list = json.loads(mcq_answers)
        
        # Process video responses
        video_data_list = []
        for video_file in interview_videos:
            video_bytes = await video_file.read()
            video_data_list.append(video_bytes)
        
        # STAGE 3: Transcribe videos + score MCQ
        interview_questions = pipeline.get_interview_questions()
        transcriptions = conduct_video_interview(interview_questions, video_data_list)
        stage3 = pipeline.run_stage3(transcriptions, mcq_answers_list)
        
        # STAGE 4: Gemini final comprehensive analysis
        stage4 = pipeline.run_stage4()
        
        # Complete and index in Qdrant
        candidate_id_final = pipeline.complete()
        
        # Clean up session
        del session_storage[candidate_id]
        
        return JSONResponse({
            "status": "success",
            "candidate_id": candidate_id_final,
            "evaluation": pipeline.get_full_evaluation(),
            "final_recommendation": stage4['recommendation'],
            "final_score": stage4['overall_score']
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation completion error: {str(e)}")

@router.post("/evaluate/full")
async def full_evaluation(
    resume: UploadFile = File(...),
    code_solution: str = Form(...),
    job_description: str = Form(...),
    ideal_candidate_profile: str = Form(...),
    task_description: str = Form(...),
    candidate_id: str = Form(...),
    jd_id: str = Form(...),
    interview_videos: List[UploadFile] = File(...),
    mcq_answers: str = Form(...)
):
    """
    Complete end-to-end evaluation in one API call.
    USE THIS FOR TESTING.
    """
    try:
        resume_text = extract_text_from_pdf(resume)
        mcq_answers_list = json.loads(mcq_answers)
        
        video_data_list = []
        for video_file in interview_videos:
            video_bytes = await video_file.read()
            video_data_list.append(video_bytes)
        
        pipeline = CandidateEvaluationPipeline(
            jd_text=job_description,
            ideal_candidate_profile=ideal_candidate_profile,
            task_description=task_description,
            candidate_id=candidate_id,
            jd_id=jd_id
        )
        
        # Execute all stages
        stage1 = pipeline.run_stage1(code_solution)
        stage2 = pipeline.run_stage2(resume_text)
        
        interview_questions = stage1['interview_questions']
        transcriptions = conduct_video_interview(interview_questions, video_data_list)
        
        stage3 = pipeline.run_stage3(transcriptions, mcq_answers_list)
        stage4 = pipeline.run_stage4()
        
        candidate_id_final = pipeline.complete()
        
        return JSONResponse({
            "status": "success",
            "candidate_id": candidate_id_final,
            "evaluation": pipeline.get_full_evaluation()
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Full evaluation error: {str(e)}")

@router.get("/evaluate/status/{candidate_id}")
async def get_evaluation_status(candidate_id: str):
    """Get current evaluation status for a candidate"""
    if candidate_id in session_storage:
        return JSONResponse({
            "status": "in_progress",
            "candidate_id": candidate_id
        })
    else:
        return JSONResponse({
            "status": "not_found",
            "message": "No active evaluation for this candidate"
        })