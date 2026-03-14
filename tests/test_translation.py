"""
Tests for the BanglaT5 translation module.

Mocks HuggingFace transformers to avoid downloading models during testing.
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import unittest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class TestBanglaTranslator(unittest.TestCase):
    """Test BanglaTranslator with mocked transformers."""

    @patch("agribot.translation.bangla_t5.AutoModelForSeq2SeqLM")
    @patch("agribot.translation.bangla_t5.AutoTokenizer")
    def _make_translator(self, mock_tokenizer_cls, mock_model_cls):
        """Helper to create a translator with mocked models."""
        # Mock tokenizer — returns a mock dict-like object with .to() support
        mock_tok = MagicMock()
        mock_encoded = MagicMock()
        mock_encoded.to.return_value = mock_encoded
        mock_tok.return_value = mock_encoded
        mock_tok.decode.return_value = "মক অনুবাদ"
        mock_tokenizer_cls.from_pretrained.return_value = mock_tok

        # Mock model
        mock_model = MagicMock()
        mock_model.generate.return_value = [MagicMock()]
        mock_model_cls.from_pretrained.return_value = mock_model

        from agribot.translation.bangla_t5 import BanglaTranslator
        translator = BanglaTranslator(device="cpu")
        return translator, mock_tok, mock_model

    def test_translator_init_loads_two_models(self):
        """Translator should load both EN→BN and BN→EN models."""
        with patch("agribot.translation.bangla_t5.AutoModelForSeq2SeqLM") as mock_model_cls, \
             patch("agribot.translation.bangla_t5.AutoTokenizer") as mock_tok_cls:
            mock_tok_cls.from_pretrained.return_value = MagicMock()
            mock_model = MagicMock()
            mock_model_cls.from_pretrained.return_value = mock_model

            from agribot.translation.bangla_t5 import BanglaTranslator
            t = BanglaTranslator(device="cpu")

            # Should call from_pretrained twice (EN→BN and BN→EN)
            assert mock_tok_cls.from_pretrained.call_count == 2
            assert mock_model_cls.from_pretrained.call_count == 2

    def test_translate_en_to_bn_empty(self):
        """Empty input should return empty string."""
        translator, _, _ = self._make_translator()
        assert translator.translate_en_to_bn("") == ""
        assert translator.translate_en_to_bn("   ") == ""

    def test_translate_bn_to_en_empty(self):
        """Empty input should return empty string."""
        translator, _, _ = self._make_translator()
        assert translator.translate_bn_to_en("") == ""
        assert translator.translate_bn_to_en("   ") == ""

    def test_translate_en_to_bn_calls_model(self):
        """Translation should tokenize, generate, and decode."""
        translator, mock_tok, mock_model = self._make_translator()
        result = translator.translate_en_to_bn("Rice blast is a fungal disease.")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_translate_bn_to_en_calls_model(self):
        """BN→EN translation should work."""
        translator, mock_tok, _ = self._make_translator()
        mock_tok.decode.return_value = "Rice blast disease"
        result = translator.translate_bn_to_en("ধানের ব্লাস্ট রোগ")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_split_sentences(self):
        """Sentence splitting should handle common patterns."""
        translator, _, _ = self._make_translator()
        sentences = translator._split_sentences(
            "Rice blast is a dangerous disease. It affects the leaves severely. Treatment should begin early in the season."
        )
        assert len(sentences) == 3
        assert "Rice blast" in sentences[0]

    def test_split_sentences_merges_short_fragments(self):
        """Very short fragments should be merged with previous sentence."""
        translator, _, _ = self._make_translator()
        sentences = translator._split_sentences("This is a full sentence. OK.")
        # "OK." is < 4 words, should merge with previous
        assert len(sentences) == 1

    def test_normalize_bn_without_normalizer(self):
        """Without normalizer, text should pass through unchanged."""
        translator, _, _ = self._make_translator()
        translator._normalizer = None
        text = "টেস্ট টেক্সট"
        assert translator._normalize_bn(text) == text

    def test_citations_preserved_in_translation(self):
        """Citation brackets should survive translation."""
        translator, mock_tok, _ = self._make_translator()
        mock_tok.decode.return_value = "অনুবাদিত পাঠ্য"
        result = translator.translate_en_to_bn("Rice blast is serious. [irri_rice.pdf p.5]")
        assert "[irri_rice.pdf p.5]" in result

    def test_translate_en_to_bn_handles_model_error(self):
        """Model errors should fallback to original text gracefully."""
        translator, mock_tok, _ = self._make_translator()
        # Make the tokenizer call raise an error
        mock_tok.side_effect = RuntimeError("GPU OOM")
        result = translator.translate_en_to_bn("A simple sentence.")
        # Should fallback to original sentence
        assert "A simple sentence." in result


class TestGetTranslator(unittest.TestCase):
    """Test the singleton factory."""

    def test_get_translator_returns_instance(self):
        """get_translator should return a BanglaTranslator."""
        with patch("agribot.translation.bangla_t5.AutoModelForSeq2SeqLM") as mock_model_cls, \
             patch("agribot.translation.bangla_t5.AutoTokenizer") as mock_tok_cls:
            mock_tok_cls.from_pretrained.return_value = MagicMock()
            mock_model_cls.from_pretrained.return_value = MagicMock()

            import agribot.translation.bangla_t5 as mod
            mod._translator = None  # Reset singleton

            from agribot.translation.bangla_t5 import get_translator, BanglaTranslator
            t = get_translator(device="cpu")
            assert isinstance(t, BanglaTranslator)

            # Reset for other tests
            mod._translator = None

    def test_get_translator_returns_same_instance(self):
        """Singleton should return the same instance."""
        with patch("agribot.translation.bangla_t5.AutoModelForSeq2SeqLM") as mock_model_cls, \
             patch("agribot.translation.bangla_t5.AutoTokenizer") as mock_tok_cls:
            mock_tok_cls.from_pretrained.return_value = MagicMock()
            mock_model_cls.from_pretrained.return_value = MagicMock()

            import agribot.translation.bangla_t5 as mod
            mod._translator = None

            from agribot.translation.bangla_t5 import get_translator
            t1 = get_translator(device="cpu")
            t2 = get_translator(device="cpu")
            assert t1 is t2

            mod._translator = None
