import os
import json
from google import genai
from google.genai import types
from typing import List, Dict
from dotenv import load_dotenv
from google.cloud import speech_v1

load_dotenv()

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

def generate_interview_audio(question, character_persona="professional_interviewer"):
    """
    Generate AI audio for interview question (using Google TTS or similar)
    
    Returns: {question, audio_url, audio_base64}
    """
    try:
        from google.cloud import texttospeech
        
        client = texttospeech.TextToSpeechClient()
        
        synthesis_input = texttospeech.SynthesisInput(text=question)
        
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Neural2-C"  # Professional voice
        )
        
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        # Return audio data
        return {
            "question": question,
            "audio": response.audio_content.hex()[:100] + "..." if response.audio_content else None
        }
    except Exception as e:
        print(f"⚠️  Audio generation failed: {str(e)}")
        return {
            "question": question,
            "audio": None
        }

def conduct_video_interview(interview_questions, video_data_list):
    """
    Transcribe video responses using Google Speech-to-Text
    
    Args:
    - interview_questions: List of questions asked
    - video_data_list: List of video file bytes
    
    Returns: List of transcribed responses
    """
    try:
        client = speech_v1.SpeechClient()
        transcriptions = []
        
        for i, video_data in enumerate(video_data_list):
            # Convert video to audio and transcribe
            # This is simplified - in production use ffmpeg to extract audio
            
            audio = speech_v1.RecognitionAudio(content=video_data)
            config = speech_v1.RecognitionConfig(
                encoding=speech_v1.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code="en-US",
            )
            
            response = client.recognize(config=config, audio=audio)
            
            transcript = ""
            for result in response.results:
                transcript += result.alternatives[0].transcript
            
            transcriptions.append(transcript)
            print(f"   ✓ Video {i+1} transcribed: {len(transcript)} chars")
        
        return transcriptions
    except Exception as e:
        print(f"⚠️  Video transcription failed: {str(e)}")
        # Return dummy transcriptions for testing
        return ["Unable to transcribe"] * len(video_data_list)

