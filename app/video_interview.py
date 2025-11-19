import os
import base64
from typing import List, Dict
from dotenv import load_dotenv

# Free-tier compatible Gemini import
import google.generativeai as genai

load_dotenv()

# Load API key
GEMINI_API_KEY = os.getenv("GENAI_API_KEY")

# Configure Gemini client
genai.configure(api_key=GEMINI_API_KEY)

# FREE TIER MODEL (supports text + PDF, NOT video)
GEMINI_MODEL = "gemini-2.0-flash"

model = genai.GenerativeModel(GEMINI_MODEL)

# --------------------------------------------------
# TEXT-TO-SPEECH (OPTIONAL)
# --------------------------------------------------
def generate_interview_audio(question: str) -> Dict:
    """
    Produce audio for the interview question using Google Cloud Text-to-Speech.
    Not required for the interview scoring pipeline.
    """
    try:
        from google.cloud import texttospeech

        tts_key_path = os.getenv("GEMINI_TTS_API_KEY")
        if tts_key_path and os.path.exists(tts_key_path):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = tts_key_path

            tts_client = texttospeech.TextToSpeechClient()

            synthesis_input = texttospeech.SynthesisInput(text=question)
            voice = texttospeech.VoiceSelectionParams(
                language_code="en-US",
                name="en-US-Neural2-J",
                ssml_gender=texttospeech.SsmlVoiceGender.MALE,
            )
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=0.95,
            )

            response = tts_client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )

            audio_base64 = base64.b64encode(response.audio_content).decode("utf-8")

            return {
                "question": question,
                "audio_base64": audio_base64,
                "mime_type": "audio/mpeg",
            }

    except Exception as e:
        print(f"⚠️ TTS generation failed: {e}")

    return {"question": question, "audio_base64": None, "mime_type": None}


# --------------------------------------------------
# REAL VIDEO TRANSCRIPTION USING GEMINI 1.5 FLASH
# --------------------------------------------------
def transcribe_video_responses(
    interview_questions: List[str], video_responses: List[bytes]
) -> List[Dict]:
    """
    REAL TRANSCRIPTION:
    Gemini 1.5 Flash can transcribe video (mp4, mov).

    Returns:
    [
      {
         "question": "...",
         "transcription": "real text"
      },
      ...
    ]
    """

    results = []

    for idx, question in enumerate(interview_questions):

        if idx < len(video_responses) and video_responses[idx]:
            print(f"🎬 Transcribing video for Q{idx+1} using Gemini 1.5 Flash...")

            video_bytes = video_responses[idx]

            try:
                # Perform real transcription using Gemini
                response = model.generate_content(
                    [
                        {
                            "mime_type": "video/mp4",
                            "data": video_bytes,
                        },
                        "Transcribe everything spoken in this video. "
                        "Return ONLY the transcription text. No commentary.",
                    ],
                    generation_config={
                        "temperature": 0.0,
                    },
                )

                transcription = response.text.strip()

                if not transcription or len(transcription) < 3:
                    transcription = "[Empty or silent video detected]"

            except Exception as e:
                print(f"❌ Transcription failed: {e}")
                transcription = "[Transcription error]"

        else:
            transcription = "[No response provided]"

        results.append(
            {
                "question": question,
                "transcription": transcription,
            }
        )

        print(f"   ✅ Q{idx+1} Transcription length: {len(transcription)} characters")
        print(f"       Transcript Preview: {transcription}...")

    return results


# --------------------------------------------------
# STRICT RESPONSE ANALYSIS (PER-ANSWER)
# --------------------------------------------------
def analyze_single_response(
    question: str, transcription: str, code_context: str
) -> Dict:
    """
    Strict scoring based PURELY on the transcript text.
    Ensures silent videos score 0.
    """

    norm = (transcription or "").strip().lower()

    placeholder_markers = [
        "no response",
        "empty",
        "silent",
        "not available",
        "[",
        "]",
        "transcription error",
    ]

    # Reject empty or placeholder answers
    if (
        not norm
        or len(norm) < 10
        or any(marker in norm for marker in placeholder_markers)
    ):
        print("⚠️ Silent/invalid response → Score = 0")
        return {
            "technical_accuracy": 0,
            "clarity": 0,
            "depth": 0,
            "communication": 0,
            "feedback": "No meaningful spoken answer detected.",
        }

    # REAL ANSWER — now score with Gemini
    prompt = f"""
You are an extremely strict technical interviewer.

Question:
{question}

Candidate Response:
{transcription}

Code Context (max 500 chars):
{code_context[:500]}

Scoring Rules:
- 1–10 scale per category
- Short answers (<15 words) = 1 to 3
- Shallow or generic answers = 1 to 4
- Deep, specific, technical = higher scores
- Be strict and avoid inflating scores.

Return ONLY valid JSON:

{{
 "technical_accuracy": int,
 "clarity": int,
 "depth": int,
 "communication": int,
 "feedback": "string"
}}
"""

    try:
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.2,
                "max_output_tokens": 300,
                "response_mime_type": "application/json",
            },
        )

        import json

        return json.loads(response.text)

    except Exception as e:
        print(f"⚠️ Scoring failed: {e}")
        return {
            "technical_accuracy": 0,
            "clarity": 0,
            "depth": 0,
            "communication": 0,
            "feedback": "Unable to analyze due to model error.",
        }


# --------------------------------------------------
# VIDEO VALIDATION
# --------------------------------------------------
def validate_video_file(video_data: bytes) -> bool:
    """Checks video size validity."""
    if not video_data or len(video_data) < 1500:
        print("⚠️ Video too small or empty")
        return False

    if len(video_data) > 50 * 1024 * 1024:  # 50MB
        print("⚠️ Video exceeds max size (50MB)")
        return False

    return True