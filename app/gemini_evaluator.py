import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv
from app.github_fetcher import fetch_github_code

load_dotenv()

GENAI_API_KEY = os.getenv("GENAI_API_KEY")
GENAI_MODEL = os.getenv("GENAI_MODEL", "gemini-flash-latest")

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


def stage1_evaluate_code(repo_link, task_description, jd_text):
    """
    STAGE 1: Gemini evaluates code from GitHub repo
    NOW ACTUALLY FETCHES THE CODE FROM GITHUB
    
    Returns:
    - code_quality_score (1-100)
    - code_description (what the code achieves)
    - interview_questions (5 specific questions about the code)
    - mcq_questions (3 questions with options)
    """
    print("🤖 Gemini evaluating code from GitHub (Stage 1)...")

    try:
        # FETCH ACTUAL CODE FROM GITHUB
        code_content = fetch_github_code(repo_link)
        
        # Truncate if too long (Gemini has token limits)
        max_code_length = 15000
        if len(code_content) > max_code_length:
            code_content = code_content[:max_code_length] + "\n\n[... Code truncated for length ...]"
        
    except Exception as e:
        print(f"❌ Could not fetch GitHub code: {str(e)}")
        raise RuntimeError(f"GitHub fetch failed: {str(e)}")

    prompt = f"""
You are an expert code reviewer and interview question generator.

TASK DESCRIPTION:
{task_description}

JOB DESCRIPTION:
{jd_text}

CANDIDATE'S CODE SUBMISSION:
{code_content}

Please analyze this code submission and provide:

1. **code_quality_score** (1-100): Rate the code based on:
   - Functionality (does it solve the task correctly?)
   - Code structure and readability
   - Error handling and edge cases
   - Performance and efficiency
   - Best practices and conventions
   - Documentation and comments

2. **code_description**: Concise description (2-3 sentences) of what this code achieves and how it solves the problem

3. **interview_questions**: Generate 5 specific interview questions about THIS EXACT CODE. Ask about:
   - Their implementation choices and why they made them
   - How they would handle specific edge cases
   - Trade-offs they considered
   - Performance optimizations they applied
   - How their solution relates to the job requirements
   
   Example: "I noticed you used a hash map in your solution. Can you explain why you chose this data structure over alternatives?"

4. **mcq_questions**: Generate 3 multiple-choice questions testing:
   - Understanding of the algorithm/approach used in THEIR code
   - Code correctness and functionality
   - Time/space complexity concepts
   
   Each question should have 4 options (A, B, C, D) and specify the correct_answer (e.g., "A")

Return valid JSON only, no markdown.
"""

    try:
        response = client.models.generate_content(
            model=GENAI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=STAGE1_SCHEMA,
                temperature=0.3,
            ),
        )

        result = json.loads(response.text)
        
        # Validate scores
        result["code_quality_score"] = max(1, min(100, result.get("code_quality_score", 50)))
        
        print(f"✅ Stage 1 complete: Code quality = {result['code_quality_score']}/100")
        print(f"✅ Generated {len(result['interview_questions'])} interview questions")
        print(f"✅ Generated {len(result['mcq_questions'])} MCQ questions")
        
        return result

    except Exception as e:
        print(f"❌ Gemini Stage 1 error: {str(e)}")
        # Return fallback
        return {
            "code_quality_score": 50,
            "code_description": "Code repository was analyzed but full evaluation could not be completed",
            "interview_questions": [
                "Can you walk me through your overall approach to solving this problem?",
                "What challenges did you face during implementation and how did you overcome them?",
                "How would you optimize this solution for better performance?",
                "Can you describe the time and space complexity of your solution?",
                "How did you test your solution to ensure it handles edge cases?",
            ],
            "mcq_questions": [
                {
                    "question": "What is the primary goal of the submitted code?",
                    "options": [
                        "To solve the coding task efficiently",
                        "To demonstrate framework knowledge",
                        "To create a web application",
                        "To process large datasets",
                    ],
                    "correct_answer": "A",
                },
                {
                    "question": "Which is most important in production code?",
                    "options": [
                        "Readability and maintainability",
                        "Using the latest frameworks",
                        "Minimizing lines of code",
                        "Adding many features",
                    ],
                    "correct_answer": "A",
                },
                {
                    "question": "What should you always consider when designing algorithms?",
                    "options": [
                        "Time and space complexity trade-offs",
                        "Using the most complex solution",
                        "Following coding trends",
                        "Maximizing code length",
                    ],
                    "correct_answer": "A",
                },
            ],
        }


def stage4_final_analysis(
    jd_text,
    resume_bytes,
    repo_link,
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
    Uses multimodal to analyze PDF resume
    Fetches GitHub code again for context
    
    Takes all scores and data, returns comprehensive evaluation
    """
    print("🎯 Gemini generating final analysis (Stage 4)...")

    # Fetch code again for context
    try:
        code_content = fetch_github_code(repo_link)
        if len(code_content) > 10000:
            code_content = code_content[:10000] + "\n\n[... truncated ...]"
    except Exception as e:
        print(f"⚠️ Could not fetch code for Stage 4: {str(e)}")
        code_content = "[Code could not be fetched]"

    prompt = f"""
You are an expert recruiter and technical hiring manager. Based on the following comprehensive evaluation data, provide a final assessment of this candidate.

========== EVALUATION SCORES ==========

- Resume Fit Score: {resume_fit_score}/100 (How well resume matches ideal candidate profile)
- Code Solution Fit Score: {code_fit_score}/100 (How well code solves the task)
- Code Quality Score: {code_quality_score}/100 (Code quality, best practices, efficiency)
- MCQ Assessment Score: {mcq_score}/100 (Technical knowledge test)

========== JOB DETAILS ==========

JOB DESCRIPTION:
{jd_text[:1000]}

TASK DESCRIPTION:
{task_description}

========== CANDIDATE'S CODE ==========

GITHUB REPOSITORY: {repo_link}

CODE SAMPLE:
{code_content}

========== INTERVIEW DATA ==========

Interview Questions Asked:
{json.dumps(interview_questions, indent=2)}

Candidate's Video Interview Responses (Transcribed):
{json.dumps(interview_transcripts, indent=2)}

========== YOUR TASK ==========

Analyze the RESUME PDF provided, the candidate's CODE, and their INTERVIEW RESPONSES to provide:

1. **video_interview_score** (1-100): Score the video interview responses based on:
   - Technical depth and accuracy of explanations
   - Communication clarity and professionalism
   - Ability to articulate their thought process
   - Demonstration of problem-solving skills
   - Alignment with job requirements
   
2. **overall_score** (1-100): Calculate weighted overall score:
   - 15% Resume Fit (how well resume matches ideal profile)
   - 15% Code Fit (how well solution addresses the task)
   - 30% Code Quality (implementation quality and best practices)
   - 25% Video Interview Performance (communication and technical depth)
   - 15% MCQ Score (technical knowledge)
   
3. **summary**: 2-3 sentence professional summary of the candidate's overall performance

4. **strengths**: List 3-5 key strengths demonstrated by the candidate across all evaluation areas

5. **weaknesses**: List 2-4 areas for improvement or concerns

6. **recommendation**: One of: "Strong Hire", "Hire", "Maybe", or "No Hire"
   - Strong Hire: 90-100 (exceptional candidate)
   - Hire: 75-89 (solid candidate, recommended)
   - Maybe: 60-74 (borderline, needs discussion)
   - No Hire: <60 (not recommended)

Return valid JSON only, no markdown.
"""

    try:
        # Send PDF resume with prompt
        response = client.models.generate_content(
            model=GENAI_MODEL,
            contents=[
                types.Part.from_bytes(
                    data=resume_bytes,
                    mime_type="application/pdf"
                ),
                prompt
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=STAGE4_SCHEMA,
                temperature=0.4,
            ),
        )

        result = json.loads(response.text)

        # Ensure scores are valid
        result["video_interview_score"] = max(1, min(100, result.get("video_interview_score", 50)))
        result["overall_score"] = max(1, min(100, result.get("overall_score", 50)))

        print(f"✅ Stage 4 complete: Overall score = {result['overall_score']}/100")
        print(f"✅ Video interview score = {result['video_interview_score']}/100")
        print(f"✅ Recommendation: {result['recommendation']}")
        
        return result

    except Exception as e:
        print(f"❌ Gemini Stage 4 error: {str(e)}")
        
        # Calculate fallback scores
        video_score = estimate_interview_quality(interview_transcripts)
        overall = int(
            (resume_fit_score * 0.15)
            + (code_fit_score * 0.15)
            + (code_quality_score * 0.30)
            + (video_score * 0.25)
            + (mcq_score * 0.15)
        )
        
        return {
            "overall_score": overall,
            "video_interview_score": video_score,
            "summary": "Candidate demonstrated technical capability across code submission and interview responses.",
            "strengths": [
                "Completed the coding challenge successfully",
                "Provided responses to all interview questions",
                "Demonstrated problem-solving approach",
            ],
            "weaknesses": [
                "Some areas need further evaluation",
                "Could improve technical communication",
            ],
            "recommendation": "Hire" if overall >= 75 else ("Maybe" if overall >= 60 else "No Hire"),
        }


def estimate_interview_quality(transcripts):
    """
    Estimate interview quality from transcripts when Gemini analysis fails
    Based on response length and substance
    """
    if not transcripts or len(transcripts) == 0:
        return 50

    try:
        total_length = sum(len(t) for t in transcripts)
        avg_length = total_length / len(transcripts)

        # Heuristic scoring
        if avg_length < 30:
            return 35  # Very short responses
        elif avg_length < 80:
            return 55  # Brief responses
        elif avg_length < 200:
            return 70  # Decent responses
        elif avg_length < 400:
            return 85  # Detailed responses
        else:
            return 90  # Very thorough responses

    except Exception:
        return 50