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
    """Orchestrates the 4-stage evaluation pipeline"""
    
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
        self.stage1_result = None
        self.stage2_result = None
        self.stage3_result = None
        self.stage4_result = None
        
        self.created_at = datetime.utcnow().isoformat()
    
    def run_stage1(self, code_solution: str) -> Dict:
        """
        Stage 1: Gemini Code Evaluation
        - Evaluates code quality and functionality
        - Generates code description
        - Creates video interview questions
        - Generates MCQ questions
        """
        print(f"\n[Stage 1] Evaluating code with Gemini...")
        self.code_solution = code_solution
        
        self.stage1_result = stage1_evaluate_code(
            code_solution=code_solution,
            task_description=self.task_description,
            jd_text=self.jd_text
        )
        
        print(f"✓ Code Quality Score: {self.stage1_result['code_quality_score']}/100")
        print(f"✓ Generated {len(self.stage1_result['interview_questions'])} interview questions")
        print(f"✓ Generated {len(self.stage1_result['mcq_questions'])} MCQ questions")
        
        return self.stage1_result
    
    def run_stage2(self, resume_content: str) -> Dict:
        """
        Stage 2: Qdrant Vector Scoring
        - Calculates resume fit score (resume vs ideal candidate)
        - Calculates code fit score (task vs code description)
        """
        print(f"\n[Stage 2] Calculating vector similarity scores...")
        self.resume_content = resume_content
        
        code_description = self.stage1_result.get('code_description', '')
        
        # Score resume fit
        resume_fit_score = self.qdrant_scorer.score_resume_fit(
            resume_text=resume_content,
            ideal_candidate_profile=self.ideal_candidate_profile,
            candidate_id=self.candidate_id
        )
        
        # Score code fit
        code_fit_score = self.qdrant_scorer.score_code_fit(
            code_description=code_description,
            task_description=self.task_description,
            candidate_id=self.candidate_id
        )
        
        self.stage2_result = {
            "resume_fit_score": resume_fit_score,
            "code_fit_score": code_fit_score
        }
        
        print(f"✓ Resume Fit Score: {resume_fit_score}/100")
        print(f"✓ Code Fit Score: {code_fit_score}/100")
        
        return self.stage2_result
    
    def run_stage3(self, interview_transcripts: List[str], mcq_answers: List[str]) -> Dict:
        """
        Stage 3: Video Interview + MCQ Assessment
        - Processes transcribed interview responses
        - Calculates MCQ score
        """
        print(f"\n[Stage 3] Processing interview and MCQ responses...")
        self.interview_transcripts = interview_transcripts
        self.mcq_answers = mcq_answers
        
        # Score MCQ
        mcq_score = self.mcq_scorer.score_mcq_answers(
            mcq_questions=self.stage1_result['mcq_questions'],
            user_answers=mcq_answers
        )
        
        self.stage3_result = {
            "mcq_score": mcq_score,
            "interview_transcripts": interview_transcripts
        }
        
        print(f"✓ MCQ Score: {mcq_score}/100")
        print(f"✓ Correct Answers: {mcq_result['correct_count']}/{mcq_result['total_count']}")
        print(f"✓ Interview Responses: {len(interview_transcripts)} transcripts")
        
        return self.stage3_result
    
    def run_stage4(self) -> Dict:
        """
        Stage 4: Gemini Final Comprehensive Analysis
        - Evaluates video interview transcripts
        - Calculates weighted overall score
        - Generates comprehensive feedback
        """
        print(f"\n[Stage 4] Generating final comprehensive analysis...")
        
        # Collect all scores
        code_quality_score = self.stage1_result['code_quality_score']
        resume_fit_score = self.stage2_result['resume_fit_score']
        code_fit_score = self.stage2_result['code_fit_score']
        mcq_score = self.stage3_result['mcq_score']
        
        interview_questions = self.stage1_result['interview_questions']
        
        # Call Gemini for final analysis
        self.stage4_result = stage4_final_analysis(
            jd_text=self.jd_text,
            resume_text=self.resume_content,
            code_solution=self.code_solution,
            task_description=self.task_description,
            resume_fit_score=resume_fit_score,
            code_fit_score=code_fit_score,
            code_quality_score=code_quality_score,
            mcq_score=mcq_score,
            interview_questions=interview_questions,
            interview_transcripts=self.interview_transcripts
        )
        
        print(f"✓ Overall Score: {self.stage4_result['overall_score']}/100")
        print(f"✓ Recommendation: {self.stage4_result['recommendation']}")
        
        return self.stage4_result
    
    def complete(self) -> str:
        """
        Complete evaluation and index candidate in Qdrant
        """
        print(f"\n[Completion] Indexing candidate...")
        
        if not self.stage4_result:
            raise ValueError("Stage 4 must be completed before completion")
        
        # Add metadata to final analysis
        final_data = {
            **self.stage4_result,
            'candidate_id': self.candidate_id,
            'jd_id': self.jd_id,
            'created_at': self.created_at,
            'completed_at': datetime.utcnow().isoformat()
        }
        
        # Index in Qdrant
        indexed_id = index_candidate(final_data, self.candidate_id)
        
        print(f"✓ Candidate indexed: {indexed_id}")
        
        return indexed_id
    
    def get_interview_questions(self) -> List[str]:
        """Get generated interview questions"""
        if not self.stage1_result:
            return []
        return self.stage1_result['interview_questions']
    
    def get_mcq_questions(self) -> List[Dict]:
        """Get generated MCQ questions"""
        if not self.stage1_result:
            return []
        return self.stage1_result['mcq_questions']
    
    def get_full_evaluation(self) -> Dict:
        """Get complete evaluation results"""
        return {
            'candidate_id': self.candidate_id,
            'jd_id': self.jd_id,
            'created_at': self.created_at,
            'stage1': self.stage1_result,
            'stage2': self.stage2_result,
            'stage3': self.stage3_result,
            'stage4': self.stage4_result
        }