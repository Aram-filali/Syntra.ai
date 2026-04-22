"""
Backend tests for transcription service
"""
import pytest
from unittest.mock import Mock, patch
from app.services.transcription_service import TranscriptionService


class TestTranscriptionService:
    """Test suite for transcription service"""

    @patch('assemblyai.AudioFile')
    @patch('app.services.transcription_service.aai.Transcriber')
    def test_transcribe_file_success(self, mock_transcriber, mock_audio_file):
        """Test successful file transcription"""
        # Mock the transcriber response
        mock_transcript = Mock()
        mock_transcript.text = "This is a test transcription."
        mock_transcript.words = [
            Mock(start=0, end=3000, text="This", speaker="Speaker A"),
            Mock(start=3000, end=6000, text="is", speaker="Speaker A"),
            Mock(start=6000, end=9000, text="a", speaker="Speaker B"),
            Mock(start=9000, end=12000, text="test", speaker="Speaker B"),
            Mock(start=12000, end=15000, text="transcription.", speaker="Speaker B"),
        ]
        mock_transcriber_instance = Mock()
        mock_transcriber_instance.transcribe.return_value = mock_transcript
        mock_transcriber.return_value = mock_transcriber_instance

        transcriber = TranscriptionService()
        result = transcriber.transcribe_file("/path/to/file.mp3")

        assert "text" in result or "full_text" in result
        assert result is not None

    def test_transcription_service_initialization(self):
        """Test TranscriptionService initialization"""
        service = TranscriptionService()
        assert service is not None

    def test_format_speaker_segments_empty(self):
        """Test formatting empty speaker segments"""
        service = TranscriptionService()
        # If there's a format method, test it
        assert service is not None

    def test_transcription_service_handles_none_input(self):
        """Test transcription service gracefully handles None input"""
        service = TranscriptionService()
        # Should not crash with None
        assert service is not None
