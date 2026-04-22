# backend/app/services/transcription_service.py
#
# Wraps the AssemblyAI SDK to handle both local file uploads and remote URLs.
# Enables speaker diarization (who said what) and automatic language detection.

import os
import assemblyai as aai
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

load_dotenv()


class TranscriptionService:
    def __init__(self):
        aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")
        self.transcriber = aai.Transcriber()

    def transcribe_file(self, file_path_or_url: str) -> Dict[str, Any]:
        """
        Transcribes an audio/video file and returns the full text + speaker segments.

        The AssemblyAI SDK handles local file uploads automatically — no manual
        pre-upload step needed. Just pass a file path or a public URL.

        Args:
            file_path_or_url: Local file path (e.g. /tmp/meeting.mp4) or remote URL.

        Returns:
            dict with:
              - full_text: Complete transcription as a single string.
              - speaker_segments: List of segments, each with speaker label, text, and timestamps.
              - status: Transcription status from AssemblyAI.
              - id: AssemblyAI transcript ID (useful for debugging).
              - language: Detected language code.
        """
        config = aai.TranscriptionConfig(
            speaker_labels=True,         # Enable speaker diarization
            speakers_expected=None,      # Let AssemblyAI auto-detect the number of speakers
            language_detection=True,     # Detect language automatically (no need to specify)
            word_boost=[]                # Can be used to boost recognition of domain-specific terms
        )

        print(f"Starting transcription for: {file_path_or_url}")
        transcript = self.transcriber.transcribe(file_path_or_url, config)

        if transcript.status == aai.TranscriptStatus.error:
            raise Exception(f"AssemblyAI Error: {transcript.error}")

        # Build a structured list of speaker turns with timestamps (milliseconds)
        speaker_segments = []
        if transcript.utterances:
            for utterance in transcript.utterances:
                speaker_segments.append({
                    "speaker": f"Speaker {utterance.speaker}" if utterance.speaker is not None else "Unknown",
                    "text": utterance.text,
                    "start": utterance.start,   # in milliseconds
                    "end": utterance.end,        # in milliseconds
                    "confidence": getattr(utterance, 'confidence', None)
                })

        return {
            "full_text": transcript.text,
            "speaker_segments": speaker_segments,
            "status": str(transcript.status),
            "id": transcript.id,
            "language": getattr(transcript, 'language_code', None)
        }

    def transcribe_audio_url(self, audio_url: str) -> Dict[str, Any]:
        """Alias kept for backward compatibility with existing callers."""
        return self.transcribe_file(audio_url)

    def upload_file(self, file_path: str) -> str:
        """
        Alias kept for backward compatibility.
        The SDK now handles uploads internally inside .transcribe(), so this is a no-op.
        """
        return file_path
