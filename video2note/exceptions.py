"""Custom exceptions for Video2Note."""


class Video2NoteError(Exception):
    """Base exception for the application."""
    pass


class TranscriptionError(Video2NoteError):
    """Exception raised for errors during the transcription process."""
    pass


class FfmpegError(TranscriptionError):
    """Exception raised for errors related to ffmpeg."""
    pass


class WhisperCppError(TranscriptionError):
    """Exception raised for errors related to whisper.cpp."""
    pass 