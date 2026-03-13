"""
Speech-to-Text using faster-whisper (CTranslate2 Whisper).

Provides offline, GPU-accelerated speech recognition with automatic
language detection (Bengali / English).

Config-driven: beam_size, VAD, language hint, and confidence threshold
are all read from config.py settings.

Confidence mapping:
    conf = max(0.0, min(1.0, 1.0 + avg_logprob))
    where avg_logprob is the mean of per-segment avg_logprob values
    returned by faster-whisper.  avg_logprob typically ranges from
    -1.0 (random noise) to 0.0 (perfect), so 1 + x maps to [0, 1].
"""

import logging
from pathlib import Path
from threading import Lock
from typing import Optional

logger = logging.getLogger(__name__)

# Singleton
_stt_instance: "SpeechToText | None" = None
_stt_lock = Lock()


class SpeechToText:
    """
    Offline Speech-to-Text using faster-whisper.

    Supports automatic language detection and Bengali/English transcription.
    Models are downloaded once and cached locally for offline use.
    """

    SUPPORTED_SIZES = ("tiny", "base", "small", "medium", "large-v3")

    def __init__(
        self,
        model_size: str = "base",
        device: str = "auto",
        compute_type: str = "auto",
        beam_size: int = 5,
        vad_filter: bool = True,
        min_silence_ms: int = 500,
        language_hint: Optional[str] = "bn",
        task: str = "transcribe",
    ):
        """
        Initialize the STT engine.

        Args:
            model_size: Whisper model size (tiny/base/small/medium/large-v3).
            device: 'cpu', 'cuda', or 'auto' (auto-detect GPU).
            compute_type: 'int8', 'float16', 'float32', or 'auto'.
            beam_size: Beam search width (higher = better quality, slower).
            vad_filter: Enable Voice Activity Detection to skip silence.
            min_silence_ms: Min silence duration for VAD segmentation.
            language_hint: Force language code or None for auto-detect.
            task: 'transcribe' or 'translate'.
        """
        if model_size not in self.SUPPORTED_SIZES:
            raise ValueError(
                f"Unsupported model size '{model_size}'. "
                f"Choose from: {self.SUPPORTED_SIZES}"
            )

        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.beam_size = beam_size
        self.vad_filter = vad_filter
        self.min_silence_ms = min_silence_ms
        self.language_hint = language_hint
        self.task = task
        self._model = None

        logger.info(
            "SpeechToText initialized (model=%s, device=%s, beam=%d, vad=%s, lang=%s)",
            model_size, device, beam_size, vad_filter, language_hint or "auto",
        )

    def _ensure_model(self):
        """Lazy-load the Whisper model on first use."""
        if self._model is not None:
            return

        try:
            from faster_whisper import WhisperModel

            logger.info("Loading faster-whisper model '%s'...", self.model_size)
            self._model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
            )
            logger.info("faster-whisper model loaded successfully")

        except ImportError:
            raise ImportError(
                "faster-whisper is not installed. "
                "Install it with: pip install faster-whisper"
            )

    def transcribe(
        self,
        audio_path: str | Path,
        language: str | None = None,
        beam_size: int | None = None,
    ) -> dict:
        """
        Transcribe an audio file to text with structured diagnostics.

        Args:
            audio_path: Path to audio file (WAV, MP3, FLAC, etc.)
            language: Force language override (or use instance default).
            beam_size: Beam size override (or use instance default).

        Returns:
            dict with keys:
                - 'text': Full transcribed text
                - 'language': Detected/forced language code
                - 'confidence': Float 0-1 mapped from avg_logprob
                - 'segments': List of segment dicts with start/end/text
                - 'warnings': List of warning strings
        """
        self._ensure_model()

        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        # Use instance defaults unless overridden
        effective_lang = language if language is not None else self.language_hint
        effective_beam = beam_size if beam_size is not None else self.beam_size

        logger.info(
            "Transcribing: %s (lang=%s, beam=%d)",
            audio_path.name, effective_lang or "auto", effective_beam,
        )

        # Build transcription kwargs
        transcribe_kwargs = {
            "language": effective_lang,
            "beam_size": effective_beam,
            "vad_filter": self.vad_filter,
            "condition_on_previous_text": False,
            "task": self.task,
            "initial_prompt": (
                "কৃষি, ধান, পোকা, সার, রোগ, পাতা, গম, কৃষিবিদ্যা. "
                "Agriculture, crops, farming, pests."
            ),
        }

        # Add VAD parameters if VAD enabled
        if self.vad_filter:
            transcribe_kwargs["vad_parameters"] = dict(
                min_silence_duration_ms=self.min_silence_ms,
            )

        segments_iter, info = self._model.transcribe(
            str(audio_path), **transcribe_kwargs
        )

        # Collect segments and compute confidence
        segment_list = []
        full_text_parts = []
        logprob_sum = 0.0
        logprob_count = 0

        for seg in segments_iter:
            text = seg.text.strip()
            if text:
                segment_list.append({
                    "start": seg.start,
                    "end": seg.end,
                    "text": text,
                    "avg_logprob": getattr(seg, "avg_logprob", -1.0),
                    "no_speech_prob": getattr(seg, "no_speech_prob", 0.0),
                })
                full_text_parts.append(text)

                # Accumulate log probabilities for confidence
                seg_logprob = getattr(seg, "avg_logprob", -1.0)
                logprob_sum += seg_logprob
                logprob_count += 1

        full_text = " ".join(full_text_parts)

        # Compute confidence: map avg_logprob [-1, 0] → [0, 1]
        if logprob_count > 0:
            avg_logprob = logprob_sum / logprob_count
            confidence = max(0.0, min(1.0, 1.0 + avg_logprob))
        else:
            avg_logprob = -1.0
            confidence = 0.0

        # Build warnings list
        warnings = _build_warnings(
            full_text=full_text,
            confidence=confidence,
            segment_list=segment_list,
            language_prob=info.language_probability,
        )

        logger.info(
            "Transcription complete: lang=%s (%.1f%%), conf=%.2f, %d chars, warnings=%s",
            info.language,
            info.language_probability * 100,
            confidence,
            len(full_text),
            warnings or "none",
        )

        return {
            "text": full_text,
            "language": info.language,
            "confidence": round(confidence, 3),
            "language_probability": info.language_probability,
            "segments": segment_list,
            "warnings": warnings,
        }

    def transcribe_numpy(
        self,
        audio_array,
        sample_rate: int = 16000,
        language: str | None = None,
    ) -> dict:
        """
        Transcribe from a numpy audio array (e.g., from microphone recording).

        Args:
            audio_array: numpy array of audio samples (float32, mono)
            sample_rate: Sample rate of the audio (default 16kHz for Whisper)
            language: Force language or None for auto-detect

        Returns:
            Same dict format as transcribe()
        """
        self._ensure_model()

        import tempfile
        import numpy as np

        # Ensure float32 mono
        if audio_array.ndim > 1:
            audio_array = audio_array.mean(axis=1)
        audio_array = audio_array.astype(np.float32)

        # Save to temp WAV file (faster-whisper reads files)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            import soundfile as sf
            sf.write(tmp.name, audio_array, sample_rate)
            tmp_path = tmp.name

        try:
            return self.transcribe(tmp_path, language=language)
        finally:
            Path(tmp_path).unlink(missing_ok=True)


def _build_warnings(
    full_text: str,
    confidence: float,
    segment_list: list[dict],
    language_prob: float,
) -> list[str]:
    """Build list of warning strings based on transcription metrics."""
    warnings: list[str] = []

    if not full_text.strip():
        warnings.append("no_speech")
        return warnings

    if confidence < 0.4:
        warnings.append("low_confidence")
    elif confidence < 0.6:
        warnings.append("moderate_confidence")

    # Check for high no-speech probability in segments
    high_nospeech = sum(
        1 for s in segment_list
        if s.get("no_speech_prob", 0) > 0.6
    )
    if high_nospeech > len(segment_list) * 0.5 and segment_list:
        warnings.append("noisy_audio")

    if language_prob < 0.7:
        warnings.append("uncertain_language")

    return warnings


def get_stt(
    model_size: str = "base",
    device: str = "auto",
    beam_size: int = 5,
    vad_filter: bool = True,
    min_silence_ms: int = 500,
    language_hint: Optional[str] = "bn",
    task: str = "transcribe",
) -> SpeechToText:
    """
    Get or create the singleton STT instance.

    Thread-safe lazy initialization.
    """
    global _stt_instance

    if _stt_instance is not None:
        return _stt_instance

    with _stt_lock:
        if _stt_instance is not None:
            return _stt_instance
        _stt_instance = SpeechToText(
            model_size=model_size,
            device=device,
            beam_size=beam_size,
            vad_filter=vad_filter,
            min_silence_ms=min_silence_ms,
            language_hint=language_hint,
            task=task,
        )

    return _stt_instance
