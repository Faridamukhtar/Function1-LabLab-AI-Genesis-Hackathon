import os
import json
from google import genai
from google.genai import types
from typing import List, Dict

GEMINI_API_KEY = os.getenv("GENAI_API_KEY")
try:
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    raise RuntimeError(f"Failed to initialize Gemini Client: {e}")

def generate_interview_audio(question: str, character_persona: str = "professional_interviewer") -> Dict:
    """
    Generate audio/text-to-speech for interview question using Gemini.
    Returns audio data and transcription.
    """
    prompt = f"""You are a professional technical interviewer conducting a video interview.
    
Character Persona: {character_persona}
Question to ask: {question}

Generate a natural, conversational way to ask this question. Keep it professional but friendly.
Return the spoken text that should be used for text-to-speech."""
    
    response = client.models.generate_content(
        model='gemini-2.0-flash-exp',
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=200
        )
    )
    
    spoken_text = response.text.strip()
    
    return {
        "question_text": question,
        "spoken_text": spoken_text,
        "character_persona": character_persona
    }

def transcribe_video_response(video_data: bytes, question: str) -> str:
    """
    Transcribe candidate's video response using Gemini's multimodal capabilities.
    """
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=[
                types.Part.from_bytes(
                    data=video_data,
                    mime_type="video/mp4"
                ),
                f"Transcribe the candidate's spoken response to this interview question: {question}\n\nExtract only the spoken words, no commentary."
            ],
            config=types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=500
            )
        )
        
        transcription = response.text.strip()
        return transcription
    except Exception as e:
        raise RuntimeError(f"Failed to transcribe video: {e}")

def conduct_video_interview(interview_questions: List[str], video_responses: List[bytes]) -> List[str]:
    """
    Conduct full video interview by processing all questions and responses.
    Returns list of transcriptions.
    """
    transcriptions = []
    
    for question, video_data in zip(interview_questions, video_responses):
        transcription = transcribe_video_response(video_data, question)
        transcriptions.append(transcription)
    
    return transcriptions

def analyze_interview_response(question: str, transcription: str, code_solution: str) -> Dict:
    """
    Analyze a single interview response for quality and technical depth.
    """
    prompt = f"""Analyze this interview response for technical depth and clarity.

Question: {question}
Candidate Response: {transcription}
Code Context: {code_solution[:500]}

Evaluate:
1. Technical accuracy (1-10)
2. Clarity of explanation (1-10)
3. Depth of understanding (1-10)
4. Communication quality (1-10)

Return JSON with scores and brief feedback."""
    
    schema = types.Schema(
        type=types.Type.OBJECT,
        properties={
            "technical_accuracy": types.Schema(type=types.Type.INTEGER),
            "clarity": types.Schema(type=types.Type.INTEGER),
            "depth": types.Schema(type=types.Type.INTEGER),
            "communication": types.Schema(type=types.Type.INTEGER),
            "feedback": types.Schema(type=types.Type.STRING)
        }
    )
    
    response = client.models.generate_content(
        model='gemini-2.0-flash-exp',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=schema,
            temperature=0.3
        )
    )
    
    return json.loads(response.text)

