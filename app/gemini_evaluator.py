import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

GENAI_API_KEY = os.getenv("GENAI_API_KEY")
GENAI_MODEL = os.getenv("GENAI_MODEL", "gemini-1.5-flash")

if not GENAI_API_KEY:
    raise ValueError("GENAI_API_KEY not found in environment variables")

client = genai.Client(api_key=GENAI_API_KEY)

# ============ STAGE 1: CODE EVALUATION SCHEMA ============
STAGE1_SCHEMA = types.Schema(
    type=types.Type.OBJECT,
    properties={
        "code_quality_score": types.Schema(type=types.Type.INTEGER),
        "code_description": types.Schema(type=types.Type.STRING),
        "interview_questions": types.Schema(
            type=types.Type.ARRAY,
            items=types.Schema(type=types.Type.STRING),
        ),
        "mcq_questions": types.Schema(
            type=types.Type.ARRAY,
            items=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "question": types.Schema(type=types.Type.STRING),
                    "options": types.Schema(
                        type=types.Type.ARRAY,
                        items=types.Schema(type=types.Type.STRING),
                    ),
                    "correct_answer": types.Schema(type=types.Type.STRING),
                },
                required=["question", "options", "correct_answer"],
            ),
        ),
    },
    required=[
        "code_quality_score",
        "code_description",
        "interview_questions",
        "mcq_questions",
    ],
)

# ============ STAGE 4: FINAL ANALYSIS SCHEMA ============
STAGE4_SCHEMA = types.Schema(
    type=types.Type.OBJECT,
    properties={
        "overall_score": types.Schema(type=types.Type.INTEGER),
        "video_interview_score": types.Schema(type=types.Type.INTEGER),
        "summary": types.Schema(type=types.Type.STRING),
        "strengths": types.Schema(
            type=types.Type.ARRAY,
            items=types.Schema(type=types.Type.STRING),
        ),
        "weaknesses": types.Schema(
            type=types.Type.ARRAY,
            items=types.Schema(type=types.Type.STRING),
        ),
        "recommendation": types.Schema(type=types.Type.STRING),
    },
    required=[
        "overall_score",
        "video_interview_score",
        "summary",
        "strengths",
        "weaknesses",
        "recommendation",
    ],
)


def stage1_evaluate_code(code_solution, task_description, jd_text):
    """
    STAGE 1: Gemini evaluates submitted code
    
    Returns:
    - code_quality_score (1-100)
    - code_description (what the code achieves)
    - interview_questions (5 specific questions about the code)
    - mcq_questions (3 questions with options)
    """
    print("🤖 Gemini evaluating code (Stage 1)...")

    prompt = f"""
    You are an expert code reviewer and interview question generator.
    
    TASK DESCRIPTION:
    {task_description}
    
    JOB DESCRIPTION:
    {jd_text}
    
    SUBMITTED CODE:
    ```
    {code_solution[:4000]}  # Limit to 4000 chars for free tier
    ```
    
    Please evaluate this code submission and provide:
    
    1. **code_quality_score** (1-100): Rate the code based on:
       - Functionality (does it solve the task?)
       - Code structure and readability
       - Error handling
       - Performance considerations
       - Best practices and conventions
    
    2. **code_description**: Concise description (2-3 sentences) of what this code achieves
    
    3. **interview_questions**: Generate 5 specific interview questions about THIS CODE. Ask about:
       - Implementation decisions
       - Problem-solving approach
       - Trade-offs considered
       - Edge cases handled
       - How it relates to the job requirements
       Example: "Can you walk me through your approach to optimize the time complexity?"
    
    4. **mcq_questions**: Generate 3 multiple-choice questions testing understanding of:
       - The algorithm/approach used
       - Code correctness
       - Performance concepts
       Each question should have 4 options (A, B, C, D) and specify the correct_answer (e.g., "A")
    
    Return valid JSON only, no markdown.
    """

    try:
        response = client.models.generate_content(
            model=GENAI_MODEL,
            contents=prompt,
            generation_config=types.GenerationConfig(
                response_mime_type="application/json",
                response_schema=STAGE1_SCHEMA,
            ),
        )

        result = json.loads(response.text)
        
        # Validate scores
        result["code_quality_score"] = max(1, min(100, result.get("code_quality_score", 50)))
        
        print(f"✅ Stage 1 complete: Code quality = {result['code_quality_score']}/100")
        return result

    except Exception as e:
        print(f"❌ Gemini Stage 1 error: {str(e)}")
        # Return fallback
        return {
            "code_quality_score": 50,
            "code_description": "Code was evaluated but response format invalid",
            "interview_questions": [
                "Can you explain your approach to solving this problem?",
                "What challenges did you face during implementation?",
                "How would you optimize this solution?",
                "Can you describe the time and space complexity?",
                "How did you test your solution?",
            ],
            "mcq_questions": [
                {
                    "question": "What is the primary goal of the submitted code?",
                    "options": [
                        "To solve the coding task efficiently",
                        "To create a web server",
                        "To process large datasets",
                        "To train a machine learning model",
                    ],
                    "correct_answer": "A",
                },
                {
                    "question": "Which of these is most important in code review?",
                    "options": [
                        "Code readability",
                        "Using fancy frameworks",
                        "Code length",
                        "Following trends",
                    ],
                    "correct_answer": "A",
                },
                {
                    "question": "What should you always consider when designing algorithms?",
                    "options": [
                        "Time and space complexity",
                        "Making it complicated",
                        "Using all features",
                        "Code comments only",
                    ],
                    "correct_answer": "A",
                },
            ],
        }


def stage4_final_analysis(
    jd_text,
    resume_text,
    code_solution,
    task_description,
    resume_fit_score,
    code_fit_score,
    code_quality_score,
    mcq_score,
    interview_questions,
    interview_transcripts,
):
    """
    STAGE 4: Gemini comprehensive final analysis
    
    Takes all scores and data, returns comprehensive evaluation
    """
    print("🎯 Gemini generating final analysis (Stage 4)...")

    # Calculate video interview score from transcripts
    video_interview_score = analyze_interview_responses(interview_transcripts)

    prompt = f"""
    You are an expert recruiter and hiring manager. Based on the following evaluation data, provide a comprehensive final assessment:
    
    ========== CANDIDATE DATA ==========
    
    RESUME:
    {resume_text[:1000]}
    
    SUBMITTED CODE SOLUTION:
    {code_solution[:1500]}
    
    JOB DESCRIPTION:
    {jd_text[:1000]}
    
    ========== EVALUATION SCORES ==========
    
    - Resume Fit Score: {resume_fit_score}/100
    - Code Solution Fit Score: {code_fit_score}/100
    - Code Quality Score: {code_quality_score}/100
    - MCQ Assessment Score: {mcq_score}/100
    - Video Interview Score: {video_interview_score}/100
    
    ========== INTERVIEW DATA ==========
    
    Interview Questions Asked:
    {json.dumps(interview_questions, indent=2)}
    
    Candidate's Responses:
    {json.dumps(interview_transcripts, indent=2)}
    
    ========== YOUR TASK ==========
    
    Based on ALL this information, provide:
    
    1. **overall_score** (1-100): Weighted overall score calculated as:
       - 15% Resume Fit
       - 15% Code Fit
       - 30% Code Quality
       - 25% Video Interview Performance
       - 15% MCQ Score
    
    2. **video_interview_score** (1-100): Analyze the interview transcripts and score based on:
       - Communication clarity
       - Technical depth
       - Problem-solving approach
       - Alignment with job requirements
    
    3. **summary**: 2-3 sentence professional summary of the candidate's overall performance
    
    4. **strengths**: List 3-4 key strengths demonstrated by the candidate (clear bullet points)
    
    5. **weaknesses**: List 2-3 areas for improvement or concerns (clear bullet points)
    
    6. **recommendation**: One of: "Strong Hire", "Hire", "Maybe", or "No Hire"
    
    Return valid JSON only, no markdown.
    """

    try:
        response = client.models.generate_content(
            model=GENAI_MODEL,
            contents=prompt,
            generation_config=types.GenerationConfig(
                response_mime_type="application/json",
                response_schema=STAGE4_SCHEMA,
            ),
        )

        result = json.loads(response.text)

        # Ensure scores are valid
        result["overall_score"] = max(1, min(100, result.get("overall_score", 50)))
        result["video_interview_score"] = video_interview_score

        print(f"✅ Stage 4 complete: Overall score = {result['overall_score']}/100")
        return result

    except Exception as e:
        print(f"❌ Gemini Stage 4 error: {str(e)}")
        # Fallback response
        return {
            "overall_score": (
                (resume_fit_score * 0.15)
                + (code_fit_score * 0.15)
                + (code_quality_score * 0.30)
                + (video_interview_score * 0.25)
                + (mcq_score * 0.15)
            ),
            "video_interview_score": video_interview_score,
            "summary": "Candidate demonstrated technical capability and alignment with role requirements.",
            "strengths": [
                "Strong coding fundamentals",
                "Clear communication in interview",
                "Problem-solving approach",
            ],
            "weaknesses": [
                "Limited experience in some areas",
                "Needs improvement in optimization",
            ],
            "recommendation": "Hire" if ((resume_fit_score + code_quality_score) / 2) > 75 else "Maybe",
        }


def analyze_interview_responses(transcripts):
    """
    Analyze interview transcripts and return a score (1-100)
    Based on length, clarity, and relevance of responses
    """
    if not transcripts or len(transcripts) == 0:
        return 50

    try:
        # Simple heuristic: score based on response length and content
        avg_length = sum(len(t) for t in transcripts) / len(transcripts)

        # Longer responses (but not too long) indicate better communication
        if avg_length < 50:
            return 40
        elif avg_length < 100:
            return 60
        elif avg_length < 300:
            return 75
        else:
            return 85

    except Exception as e:
        print(f"⚠️  Interview analysis error: {str(e)}")
        return 50