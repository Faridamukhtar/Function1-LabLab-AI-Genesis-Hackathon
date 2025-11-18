import json
from typing import Dict, List
from datetime import datetime
from app.gemini_evaluator import (
    stage1_evaluate_code,
    stage4_final_analysis
)
from app.qdrant_scorer import QdrantScorer
from app.mcq_scorer import MCQScorer


class CandidateEvaluationPipeline:
    """
    Orchestrates the evaluation pipeline with correct flow:
    
    STAGE 1 (at /evaluate/start):
    - Gemini: Fetch GitHub code → Evaluate quality → Generate code description
    - Gemini: Generate 5 video interview questions (specific to their code)
    - Gemini: Generate 3 MCQ questions
    - Qdrant: Calculate resume_fit_score (resume vs ideal candidate profile)
    - Qdrant: Calculate code_fit_score (code description vs task description)
    → Returns: interview questions, MCQs, initial scores
    
    STAGE 2 (Frontend - Candidate takes interview):
    - Play interview questions (with optional TTS audio)
    - Record video responses
    - Display MCQ questions
    - Collect MCQ answers
    
    STAGE 3 (at /evaluate/submit-responses):
    - Gemini: Transcribe video responses
    - MCQ Scorer: Score MCQ answers deterministically
    - Gemini: Final comprehensive analysis
    - Calculate weighted overall score
    → Returns: Complete evaluation results
    """
    
    def __init__(
        self,
        jd_text: str,
        ideal_candidate_profile: str,
        task_description: str,
        candidate_id: str,
        jd_id: str
    ):
        self.jd_text = jd_text
        self.ideal_candidate_profile = ideal_candidate_profile
        self.task_description = task_description
        self.candidate_id = candidate_id
        self.jd_id = jd_id
        
        self.qdrant_scorer = QdrantScorer()
        self.mcq_scorer = MCQScorer()
        
        # Stage results storage
        self.stage1_result = None  # Code eval + questions
        self.resume_fit_score = None
        self.code_fit_score = None
        self.mcq_score = None
        self.video_interview_score = None
        self.stage4_result = None  # Final analysis
        
        # Store data for later stages
        self.resume_bytes = None
        self.repo_link = None
        self.interview_transcripts = None
        
        self.created_at = datetime.utcnow().isoformat()
    
    def run_stage1(self, repo_link: str, resume_bytes: bytes) -> Dict:
        """
        STAGE 1: Complete initial evaluation
        
        1. Gemini evaluates GitHub code
        2. Gemini generates code description
        3. Gemini generates interview questions (specific to their code)
        4. Gemini generates MCQ questions
        5. Qdrant calculates resume fit score
        6. Qdrant calculates code fit score
        
        Returns: Questions and initial scores for frontend
        """
        print(f"\n{'='*60}")
        print(f"[STAGE 1] Initial Evaluation for {self.candidate_id}")
        print(f"{'='*60}")
        
        self.repo_link = repo_link
        self.resume_bytes = resume_bytes
        
        # 1. GEMINI: Evaluate code from GitHub
        print(f"\n🤖 [1/3] Gemini evaluating code from GitHub...")
        self.stage1_result = stage1_evaluate_code(
            repo_link=repo_link,
            task_description=self.task_description,
            jd_text=self.jd_text
        )
        
        code_quality_score = self.stage1_result['code_quality_score']
        code_description = self.stage1_result['code_description']
        interview_questions = self.stage1_result['interview_questions']
        mcq_questions = self.stage1_result['mcq_questions']
        
        print(f"   ✅ Code Quality Score: {code_quality_score}/100")
        print(f"   ✅ Generated {len(interview_questions)} interview questions")
        print(f"   ✅ Generated {len(mcq_questions)} MCQ questions")
        
        # 2. QDRANT: Calculate resume fit score
        print(f"\n📊 [2/3] Calculating resume fit score...")
        self.resume_fit_score = self.qdrant_scorer.score_resume_fit(
            resume_bytes=resume_bytes,
            ideal_candidate_profile=self.ideal_candidate_profile,
            candidate_id=self.candidate_id
        )
        print(f"   ✅ Resume Fit Score: {self.resume_fit_score}/100")
        
        # 3. QDRANT: Calculate code fit score
        print(f"\n📊 [3/3] Calculating code fit score...")
        self.code_fit_score = self.qdrant_scorer.score_code_fit(
            code_description=code_description,
            task_description=self.task_description,
            candidate_id=self.candidate_id
        )
        
        print(f"   ✅ Code Fit Score: {self.code_fit_score}/100")
        
        print(f"\n{'='*60}")
        print(f"✅ STAGE 1 COMPLETE")
        print(f"{'='*60}\n")
        
        return {
            "code_quality_score": code_quality_score,
            "code_description": code_description,
            "interview_questions": interview_questions,
            "mcq_questions": mcq_questions,
            "resume_fit_score": self.resume_fit_score,
            "code_fit_score": self.code_fit_score
        }
    
    def run_stage3(self, interview_videos: List[bytes], mcq_answers: List[str]) -> Dict:
        """
        STAGE 3: Process responses and generate final evaluation
        
        1. Gemini transcribes video responses
        2. Score MCQ answers deterministically
        3. Gemini performs final comprehensive analysis
        4. Calculate weighted overall score
        
        Returns: Complete evaluation results
        """
        print(f"\n{'='*60}")
        print(f"[STAGE 3] Final Evaluation for {self.candidate_id}")
        print(f"{'='*60}")
        
        if not self.stage1_result:
            raise ValueError("Stage 1 must be completed first")
        
        interview_questions = self.stage1_result['interview_questions']
        mcq_questions = self.stage1_result['mcq_questions']
        
        # 1. GEMINI: Transcribe video responses
        print(f"\n🎬 [1/3] Transcribing video interview responses...")
        from app.video_interview import transcribe_video_responses
        
        self.interview_transcripts = transcribe_video_responses(
            interview_questions=interview_questions,
            video_responses=interview_videos
        )
        
        print(f"   ✅ Transcribed {len(self.interview_transcripts)} video responses")
        for i, transcript in enumerate(self.interview_transcripts):
            print(f"   📝 Response {i+1}: {len(transcript)} characters")
            print(f"       Transcript Preview: {transcript}...")
        
        # 2. MCQ SCORER: Score MCQ answers
        print(f"\n📝 [2/3] Scoring MCQ answers...")
        mcq_result = self.mcq_scorer.score_mcq_answers(
            mcq_questions=mcq_questions,
            user_answers=mcq_answers
        )
        
        self.mcq_score = mcq_result['score']
        print(f"   ✅ MCQ Score: {self.mcq_score}/100")
        print(f"   ✅ Correct: {mcq_result['correct_count']}/{mcq_result['total_count']}")
        
        # 3. GEMINI: Final comprehensive analysis
        print(f"\n🎯 [3/3] Gemini generating final comprehensive analysis...")
        self.stage4_result = stage4_final_analysis(
            jd_text=self.jd_text,
            resume_bytes=self.resume_bytes,
            repo_link=self.repo_link,
            task_description=self.task_description,
            resume_fit_score=self.resume_fit_score,
            code_fit_score=self.code_fit_score,
            code_quality_score=self.stage1_result['code_quality_score'],
            mcq_score=self.mcq_score,
            interview_questions=interview_questions,
            interview_transcripts=self.interview_transcripts
        )
        
        self.video_interview_score = self.stage4_result['video_interview_score']
        overall_score = self.stage4_result['overall_score']
        
        print(f"   ✅ Video Interview Score: {self.video_interview_score}/100")
        print(f"   ✅ Overall Score: {overall_score}/100")
        print(f"   ✅ Recommendation: {self.stage4_result['recommendation']}")
        
        print(f"\n{'='*60}")
        print(f"✅ STAGE 3 COMPLETE - EVALUATION FINISHED")
        print(f"{'='*60}\n")
        
        return {
            "overall_score": overall_score,
            "video_interview_score": self.video_interview_score,
            "recommendation": self.stage4_result['recommendation'],
            "summary": self.stage4_result['summary'],
            "strengths": self.stage4_result['strengths'],
            "weaknesses": self.stage4_result['weaknesses'],
            "scores": {
                "code_quality": self.stage1_result['code_quality_score'],
                "resume_fit": self.resume_fit_score,
                "code_fit": self.code_fit_score,
                "mcq": self.mcq_score,
                "video_interview": self.video_interview_score
            }
        }
    
    def get_full_evaluation(self) -> Dict:
        """Get complete evaluation results for storage/reporting"""
        return {
            'candidate_id': self.candidate_id,
            'jd_id': self.jd_id,
            'created_at': self.created_at,
            'completed_at': datetime.utcnow().isoformat(),
            'repo_link': self.repo_link,
            'code_quality_score': self.stage1_result['code_quality_score'],
            'code_description': self.stage1_result['code_description'],
            'resume_fit_score': self.resume_fit_score,
            'code_fit_score': self.code_fit_score,
            'mcq_score': self.mcq_score,
            'video_interview_score': self.video_interview_score,
            'overall_score': self.stage4_result['overall_score'],
            'recommendation': self.stage4_result['recommendation'],
            'summary': self.stage4_result['summary'],
            'strengths': self.stage4_result['strengths'],
            'weaknesses': self.stage4_result['weaknesses'],
            "interview_transcripts": self.interview_transcripts
        }