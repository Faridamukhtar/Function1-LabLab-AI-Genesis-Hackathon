import json
import os
from google import genai
from google.genai import types

# Initialize Gemini Client
GEMINI_API_KEY = os.getenv("GENAI_API_KEY")
try:
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    raise RuntimeError(f"Failed to initialize Gemini Client: {e}")

STAGE1_SCHEMA = types.Schema(
    type=types.Type.OBJECT,
    properties={
        "code_quality_score": types.Schema(type=types.Type.INTEGER),
        "code_description": types.Schema(type=types.Type.STRING),
        "interview_questions": types.Schema(
            type=types.Type.ARRAY,
            items=types.Schema(type=types.Type.STRING)
        ),
        "mcq_questions": types.Schema(
            type=types.Type.ARRAY,
            items=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "question": types.Schema(type=types.Type.STRING),
                    "options": types.Schema(
                        type=types.Type.ARRAY,
                        items=types.Schema(type=types.Type.STRING)
                    ),
                    "correct_answer": types.Schema(type=types.Type.STRING)
                }
            )
        )
    },
    required=["code_quality_score", "code_description", "interview_questions", "mcq_questions"]
)

FINAL_SCHEMA = types.Schema(
    type=types.Type.OBJECT,
    properties={
        "overall_score": types.Schema(type=types.Type.INTEGER),
        "summary": types.Schema(type=types.Type.STRING),
        "resume_fit_score": types.Schema(type=types.Type.INTEGER),
        "code_fit_score": types.Schema(type=types.Type.INTEGER),
        "code_quality_score": types.Schema(type=types.Type.INTEGER),
        "video_interview_score": types.Schema(type=types.Type.INTEGER),
        "mcq_score": types.Schema(type=types.Type.INTEGER),
        "strengths": types.Schema(
            type=types.Type.ARRAY,
            items=types.Schema(type=types.Type.STRING)
        ),
        "weaknesses": types.Schema(
            type=types.Type.ARRAY,
            items=types.Schema(type=types.Type.STRING)
        ),
        "recommendation": types.Schema(type=types.Type.STRING)
    },
    required=["overall_score", "summary", "resume_fit_score", "code_fit_score", 
              "code_quality_score", "video_interview_score", "mcq_score", 
              "strengths", "weaknesses", "recommendation"]
)

def stage1_evaluate_code(code_solution, task_description, jd_text):
    prompt = f"""Evaluate this code submission and generate interview questions.

JOB DESCRIPTION:
{jd_text}

TASK:
{task_description}

CODE:
{code_solution}

Generate:
1. code_quality_score (1-100): Evaluate functionality, efficiency, code quality
2. code_description: 2-3 sentences explaining what the code does and how
3. interview_questions: 5-7 targeted questions about THIS specific code
4. mcq_questions: 5 multiple choice questions (4 options each, mark correct answer as A/B/C/D)

Return valid JSON only."""
    
    response = client.models.generate_content(
        model='gemini-2.0-flash-exp',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=STAGE1_SCHEMA,
            temperature=0.3
        )
    )
    return json.loads(response.text)

def stage4_final_analysis(jd_text, resume_text, code_solution, task_description,
                          resume_fit_score, code_fit_score, code_quality_score, 
                          mcq_score, interview_questions, interview_transcripts):
    
    interview_qa = "\n".join([f"Q: {q}\nA: {a}" for q, a in zip(interview_questions, interview_transcripts)])
    
    prompt = f"""Final comprehensive candidate analysis.

JOB DESCRIPTION:
{jd_text}

RESUME:
{resume_text}

TASK:
{task_description}

CODE:
{code_solution}

SCORES (Fixed Inputs):
- Resume Fit (Qdrant): {resume_fit_score}/100
- Code Fit (Qdrant): {code_fit_score}/100
- Code Quality (Stage 1): {code_quality_score}/100
- MCQ Score: {mcq_score}/100

VIDEO INTERVIEW Q&A:
{interview_qa}

TASKS:
1. video_interview_score (1-100): Evaluate technical depth, clarity, communication from transcripts
2. overall_score: Calculate weighted average:
   - 15% × resume_fit_score
   - 15% × code_fit_score
   - 30% × code_quality_score
   - 25% × video_interview_score
   - 15% × mcq_score
3. summary: 2-3 paragraph comprehensive summary
4. strengths: 4-6 specific evidence-based strengths
5. weaknesses: 3-5 areas for improvement
6. recommendation: "Strong Hire" (90-100) | "Hire" (75-89) | "Maybe" (60-74) | "No Hire" (<60)
7. Pass through: resume_fit_score={resume_fit_score}, code_fit_score={code_fit_score}, code_quality_score={code_quality_score}, mcq_score={mcq_score}

Return valid JSON only."""
    
    response = client.models.generate_content(
        model='gemini-2.0-flash-exp',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=FINAL_SCHEMA,
            temperature=0.2
        )
    )
    return json.loads(response.text)