import json
import os
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GENAI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")  # Free tier model

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

def _call_gemini_with_retry(prompt, schema, temperature=0.3, max_retries=3):
    """Call Gemini API with exponential backoff retry logic for rate limits"""
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=schema,
                    temperature=temperature
                )
            )
            return response
        except Exception as e:
            error_str = str(e)
            
            # Check for quota/rate limit errors
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 30  # 30s, 60s, 120s
                    print(f"⏳ Rate limited. Waiting {wait_time}s before retry {attempt + 1}/{max_retries}")
                    time.sleep(wait_time)
                    continue
                else:
                    raise RuntimeError(
                        f"Gemini API quota exhausted after {max_retries} retries. "
                        "Please wait a few minutes and try again, or upgrade to paid plan at https://ai.google.dev/billing"
                    )
            else:
                raise RuntimeError(f"Gemini API error: {str(e)}")

def stage1_evaluate_code(code_solution, task_description, jd_text):
    """STAGE 1: Evaluate code quality and generate interview questions"""
    
    # Truncate code if too long (free tier has input limits)
    max_code_length = 8000
    if len(code_solution) > max_code_length:
        code_solution = code_solution[:max_code_length] + "\n... (code truncated)"
    
    prompt = f"""Evaluate this code submission and generate interview questions.

JOB DESCRIPTION:
{jd_text[:2000]}

TASK:
{task_description[:1000]}

CODE:
{code_solution}

Generate:
1. code_quality_score (1-100): Evaluate functionality, efficiency, code quality
2. code_description: 2-3 sentences explaining what the code does and how
3. interview_questions: 5 targeted questions about THIS specific code
4. mcq_questions: 3 multiple choice questions (4 options each, mark correct answer as A/B/C/D)

Return valid JSON only."""
    
    response = _call_gemini_with_retry(prompt, STAGE1_SCHEMA, temperature=0.3)
    return json.loads(response.text)

def stage4_final_analysis(jd_text, resume_text, code_solution, task_description,
                          resume_fit_score, code_fit_score, code_quality_score, 
                          mcq_score, interview_questions, interview_transcripts):
    """STAGE 4: Generate final comprehensive analysis and score"""
    
    # Truncate inputs for free tier
    jd_text = jd_text[:1500]
    resume_text = resume_text[:1500]
    code_solution = code_solution[:2000]
    task_description = task_description[:800]
    
    interview_qa = "\n".join([f"Q: {q}\nA: {a[:300]}" for q, a in zip(interview_questions[:5], interview_transcripts[:5])])
    
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
- Resume Fit: {resume_fit_score}/100
- Code Fit: {code_fit_score}/100
- Code Quality: {code_quality_score}/100
- MCQ Score: {mcq_score}/100

VIDEO INTERVIEW Q&A:
{interview_qa}

TASKS:
1. video_interview_score (1-100): Evaluate technical depth, clarity, communication
2. overall_score: Calculate weighted average:
   - 15% × {resume_fit_score}
   - 15% × {code_fit_score}
   - 30% × {code_quality_score}
   - 25% × video_interview_score
   - 15% × {mcq_score}
3. summary: 2-3 sentence summary
4. strengths: 3-4 specific strengths
5. weaknesses: 2-3 areas for improvement
6. recommendation: "Strong Hire" (90+) | "Hire" (75-89) | "Maybe" (60-74) | "No Hire" (<60)

Return valid JSON only."""
    
    response = _call_gemini_with_retry(prompt, FINAL_SCHEMA, temperature=0.2)
    return json.loads(response.text)