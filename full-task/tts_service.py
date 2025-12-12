import os
import torch
import torchaudio
from datetime import datetime
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
import uuid
from typing import Optional, Dict, Any, Tuple
import re
from minio_resolver import resolve_path

# --- import for text splitting ---
try:
    import spacy
    # from spacy.lang.ar import Arabic # Not explicitly needed if using load_arabic_spacy()
except ImportError:
    pass  # Handle later in load_arabic_spacy

# Import all specific paths from config
from config import (
    SERIOUS_SPEAKER_REFERENCE, SERIOUS_CONFIG_PATH, SERIOUS_CHECKPOINT_PATH,
    LIVELY_SPEAKER_REFERENCE, LIVELY_CONFIG_PATH, LIVELY_CHECKPOINT_PATH,
    OUTPUT_DIR, TOKENIZER_PATH
)

# ============ Global Model and Latents ============
tts_models: Dict[str, Xtts] = {}
model_latents: Dict[str, Tuple[Any, Any]] = {}
# General Configs for Inference (based on the notebook)
SAMPLE_RATE = 24000
CROSSFADE_MS = 80
MAX_CHUNK_LENGTH = 166

# Regex for cleaning text
_whitespace_re = re.compile(r"\s+")
# Global Spacy object (initialized once)
nlp_arabic = None


# ============ TTS Model Loading and Status ============

def is_tts_ready() -> bool:
    """Check if at least one required TTS model has been loaded."""
    # Checks for the 'normal'/'lively' model
    return 'normal' in tts_models


def _load_model_and_latents(voice_type: str, checkpoint_path: str, speaker_ref: str, config_path: str) -> Optional[
    Tuple[Xtts, Tuple[Any, Any]]]:

    print(f"Current working directory: {os.getcwd()}")
    print(f"Absolute config path: {os.path.abspath(config_path)}")
    print(f"Config file exists: {os.path.exists(config_path)}")

    """Helper to initialize a single TTS model and compute its latents."""

    print("\n" + "=" * 70)
    print(f"[DEBUG] SERVER FAILS HERE: _load_model_and_latents - Loading {voice_type.upper()} Model")
    print("=" * 70)

    # Method Parameters
    print(f"[DEBUG] Method Parameters:")
    print(f"[DEBUG]   voice_type: '{voice_type}'")
    print(f"[DEBUG]   checkpoint_path: '{checkpoint_path}'")
    print(f"[DEBUG]   speaker_ref: '{speaker_ref}'")
    print(f"[DEBUG]   config_path: '{config_path}'")
    print(f"[DEBUG]   TOKENIZER_PATH (from config): '{TOKENIZER_PATH}'")

    # File Existence Checks (Raw Paths)
    print(f"\n[DEBUG] Raw Path Existence:")
    print(f"[DEBUG]   config_path exists: {os.path.exists(config_path)}")
    print(f"[DEBUG]   checkpoint_path exists: {os.path.exists(checkpoint_path)}")
    print(f"[DEBUG]   speaker_ref exists: {os.path.exists(speaker_ref)}")
    print(f"[DEBUG]   TOKENIZER_PATH exists: {os.path.exists(TOKENIZER_PATH)}")

    try:
        print(f"Loading {voice_type} TTS model...")

        # Resolve and debug config path
        resolved_config_path = resolve_path(config_path)
        print(f"[DEBUG]   Raw config_path: '{config_path}'")
        print(f"[DEBUG]   Resolved config_path: '{resolved_config_path}'")
        print(f"[DEBUG]   Resolved config exists: {os.path.exists(resolved_config_path)}")

        config = XttsConfig()
        config.load_json(resolve_path(config_path))  # Use the specific config path

        # Resolve and debug checkpoint path
        resolved_checkpoint_path = resolve_path(checkpoint_path)
        print(f"[DEBUG]   Raw checkpoint_path: '{checkpoint_path}'")
        print(f"[DEBUG]   Resolved checkpoint_path: '{resolved_checkpoint_path}'")
        print(f"[DEBUG]   Resolved checkpoint exists: {os.path.exists(resolved_checkpoint_path)}")

        # Resolve and debug tokenizer path
        resolved_tokenizer_path = resolve_path(TOKENIZER_PATH)
        print(f"[DEBUG]   Raw TOKENIZER_PATH: '{TOKENIZER_PATH}'")
        print(f"[DEBUG]   Resolved TOKENIZER_PATH: '{resolved_tokenizer_path}'")
        print(f"[DEBUG]   Resolved tokenizer exists: {os.path.exists(resolved_tokenizer_path)}")

        # Extract the directory from checkpoint path
        checkpoint_dir = os.path.dirname(resolved_checkpoint_path)
        print(f"[DEBUG]   Derived checkpoint_dir: '{checkpoint_dir}'")

        tts_model = Xtts.init_from_config(config)
        print(f"[DEBUG]   loaded tts_model")
        # print(f"[DEBUG]   tts_model: {tts_model}")
        print("[DEBUG] checkpoint size:", os.path.getsize(resolved_checkpoint_path))
        print("[DEBUG] tokenizer size:", os.path.getsize(resolved_tokenizer_path))
        tts_model.load_checkpoint(
            config,
            checkpoint_dir=checkpoint_dir,
            checkpoint_path=resolved_checkpoint_path,
            vocab_path=resolved_tokenizer_path,
            use_deepspeed=False
        )
        print(f"[DEBUG]   loaded checkpoint")

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"[DEBUG]   loaded device: {device}")
        tts_model.to(device)
        print(f"[DEBUG]   assigned device to tts_model")
        tts_model.eval()

        print(f"Computing {voice_type} speaker latents from {speaker_ref}...")
        gpt_cond_latent, speaker_embedding = tts_model.get_conditioning_latents(
            audio_path=[resolve_path(speaker_ref)]
        )

        print(f"✓ {voice_type.capitalize()} TTS model loaded on {device}")
        return tts_model, (gpt_cond_latent, speaker_embedding)
    except Exception as e:
        print(f"✗ Error loading {voice_type} TTS model: {e}")
        import traceback
        traceback.print_exc()
        return None


def initialize_tts():
    """Initialize both TTS models on startup"""
    global tts_models, model_latents, nlp_arabic

    print("\n" + "=" * 70)
    print("[DEBUG] initialize_tts - Starting TTS Initialization")
    print("=" * 70)
    print(f"[DEBUG] Config Constants:")
    print(f"[DEBUG]   LIVELY_CONFIG_PATH: '{LIVELY_CONFIG_PATH}'")
    print(f"[DEBUG]   LIVELY_CHECKPOINT_PATH: '{LIVELY_CHECKPOINT_PATH}'")
    print(f"[DEBUG]   LIVELY_SPEAKER_REFERENCE: '{LIVELY_SPEAKER_REFERENCE}'")
    print(f"[DEBUG]   SERIOUS_CONFIG_PATH: '{SERIOUS_CONFIG_PATH}'")
    print(f"[DEBUG]   SERIOUS_CHECKPOINT_PATH: '{SERIOUS_CHECKPOINT_PATH}'")
    print(f"[DEBUG]   SERIOUS_SPEAKER_REFERENCE: '{SERIOUS_SPEAKER_REFERENCE}'")
    print(f"[DEBUG]   TOKENIZER_PATH: '{TOKENIZER_PATH}'")
    print(f"[DEBUG]   OUTPUT_DIR: '{OUTPUT_DIR}'")
    print("=" * 70)

    # Initialize Spacy once
    nlp_arabic = load_arabic_spacy()

    successful_init = True

    # 1. Initialize LIVELY voice model (key is 'normal' for app.py compatibility)
    result_normal = _load_model_and_latents(
        'normal',
        LIVELY_CHECKPOINT_PATH,
        LIVELY_SPEAKER_REFERENCE,
        LIVELY_CONFIG_PATH
    )
    if result_normal:
        tts_models['normal'], model_latents['normal'] = result_normal
    else:
        successful_init = False

    # 2. Initialize SERIOUS voice model
    result_serious = _load_model_and_latents(
        'serious',
        SERIOUS_CHECKPOINT_PATH,
        SERIOUS_SPEAKER_REFERENCE,
        SERIOUS_CONFIG_PATH
    )
    if result_serious:
        tts_models['serious'], model_latents['serious'] = result_serious
    else:
        successful_init = False

    return successful_init


# ============ Text Splitting and Crossfade Logic (from TTS team update) ============

def load_arabic_spacy():
    """Load spacy for Arabic sentence segmentation if failed go to regex"""
    try:
        import spacy
        from spacy.lang.ar import Arabic
        nlp = Arabic()
        nlp.add_pipe("sentencizer")
        return nlp
    except ImportError:
        print("spacy not installed. Using regex-based sentence splitting.")
        return None
    except Exception as e:
        print(f"Could not load spacy: {e}")
        return None


def split_arabic_text_with_spacy(text):
    """Split Arabic text using spacy"""
    global nlp_arabic

    if nlp_arabic is None:
        print("Warning: spaCy model not loaded, cannot use spaCy splitter.")
        return []

    doc = nlp_arabic(text)  # Line 139: This is now safe
    sentences = []
    for sent in doc.sents:
        clean_sent = _whitespace_re.sub(" ", sent.text.strip())
        if clean_sent:
            sentences.append(clean_sent)
    return sentences


def split_arabic_text_with_regex(text):
    """Fallback Split Arabic text using regex patterns for Arabic punctuation"""
    arabic_punctuation = r"[.!?؟;؛،]+"
    sentences = []
    current = []

    for char in text:
        current.append(char)
        if re.match(arabic_punctuation, char):
            if len(text) > len(''.join(current)):
                next_char = text[len(''.join(current))]
                if next_char in ' \t\n' or len(''.join(current)) == len(text):
                    sentence = ''.join(current).strip()
                    if sentence:
                        sentences.append(_whitespace_re.sub(" ", sentence))
                    current = []

    if current:
        sentence = ''.join(current).strip()
        if sentence:
            sentences.append(_whitespace_re.sub(" ", sentence))

    return sentences


def wrap_long_arabic_sentence(sentence, max_length):
    """Wrap a long Arabic sentence to fit within max length"""
    if len(sentence) <= max_length:
        return [sentence]
    wrapped = []
    split_points = [' و', '،', ';', '؛', ' أو ', ' ثم ', ' ف', ' لأن ', ' إذا ']
    remaining = sentence
    while len(remaining) > max_length:
        found_split = False
        for splitter in split_points:
            search_text = remaining[:max_length]
            if splitter in search_text:
                split_pos = search_text.rfind(splitter)
                if split_pos > max_length // 3:
                    part = remaining[:split_pos + len(splitter)].strip()
                    if part:
                        wrapped.append(part)
                    remaining = remaining[split_pos + len(splitter):].strip()
                    found_split = True
                    break

        if not found_split:
            last_space = remaining[:max_length].rfind(' ')
            if last_space > max_length // 2:
                part = remaining[:last_space].strip()
                if part:
                    wrapped.append(part)
                remaining = remaining[last_space:].strip()
            else:
                part = remaining[:max_length].strip()
                if part:
                    wrapped.append(part)
                remaining = remaining[max_length:].strip()

    if remaining:
        wrapped.append(remaining.strip())

    return wrapped


def split_arabic_text_for_tts(text, max_length=MAX_CHUNK_LENGTH, use_spacy=True):
    """Main Splitter, split text into chunks"""
    global nlp_arabic

    if not text or not text.strip():
        return []

    text = text.strip()

    if len(text) <= max_length:
        return [_whitespace_re.sub(" ", text)]

    sentences = []

    if use_spacy and nlp_arabic:
        sentences = split_arabic_text_with_spacy(text)

    if not sentences:
        sentences = split_arabic_text_with_regex(text)

    if not sentences:
        sentences = [text]

    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(sentence) > max_length:
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""

            wrapped_parts = wrap_long_arabic_sentence(sentence, max_length)
            for part in wrapped_parts:
                chunks.append(part.strip())

        else:
            if not current_chunk:
                current_chunk = sentence
            elif len(current_chunk) + 1 + len(sentence) <= max_length:
                current_chunk = current_chunk + " " + sentence
            else:
                chunks.append(current_chunk.strip())
                current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk.strip())

    chunks = [chunk for chunk in chunks if chunk]

    return chunks


def crossfade_audio(wav_a, wav_b, fade_ms=CROSSFADE_MS, sample_rate=SAMPLE_RATE):
    """Apply crossfade between two audio segments"""

    if wav_a.shape[1] == 0:
        return wav_b
    if wav_b.shape[1] == 0:
        return wav_a

    fade_samples = int(sample_rate * fade_ms / 1000)
    fade_samples = min(fade_samples, wav_a.shape[1], wav_b.shape[1])

    if fade_samples <= 0:
        return torch.cat([wav_a, wav_b], dim=1)

    fade_out = torch.linspace(1.0, 0.0, fade_samples, device=wav_a.device).unsqueeze(0)
    a_faded = wav_a[:, -fade_samples:] * fade_out

    fade_in = torch.linspace(0.0, 1.0, fade_samples, device=wav_b.device).unsqueeze(0)
    b_faded = wav_b[:, :fade_samples] * fade_in

    crossfade_section = a_faded + b_faded

    combined = torch.cat([
        wav_a[:, :-fade_samples],
        crossfade_section,
        wav_b[:, fade_samples:]
    ], dim=1)

    return combined


def tts_arabic(prompt: str,
               model: Xtts,
               gpt_cond_latent: torch.Tensor,
               speaker_embedding: torch.Tensor,
               output_name: str,
               temperature: float = 0.7,
               speed: float = 1.0,
               max_chunk_length: int = MAX_CHUNK_LENGTH,
               crossfade_ms: int = CROSSFADE_MS):
    """
    Main TTS generation function using external text splitting and crossfading.

    Returns the path to the combined audio file.
    """

    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("Input text must be a non-empty Arabic string")

    # Split text into chunks
    print(f"Processing Arabic text ({len(prompt)} characters)...")
    chunks = split_arabic_text_for_tts(prompt, max_chunk_length, use_spacy=True)

    if not chunks:
        raise RuntimeError("No text chunks were created from input.")

    print(f"Split into {len(chunks)} chunk(s)")

    # Generate audio for each chunk
    audio_chunks = []

    for i, chunk_text in enumerate(chunks):
        # print(f"Generating audio for chunk {i+1}/{len(chunks)}...") # Suppressed for cleaner logs

        result = model.inference(
            text=chunk_text,
            language="ar",
            gpt_cond_latent=gpt_cond_latent,
            speaker_embedding=speaker_embedding,
            temperature=temperature,
            speed=speed,
            enable_text_splitting=False  # Ensure the model's internal splitting is off
        )

        wav_data = torch.tensor(result["wav"], dtype=torch.float32)

        if wav_data.ndim == 1:
            wav_data = wav_data.unsqueeze(0)

        audio_chunks.append(wav_data)

    # Combine all audio chunks with crossfade
    print("Combining audio chunks...")
    combined_audio = audio_chunks[0]

    for next_chunk in audio_chunks[1:]:
        combined_audio = crossfade_audio(combined_audio, next_chunk, crossfade_ms, SAMPLE_RATE)

    # Save the combined audio
    combined_filename = f"{output_name}.wav"
    combined_path = os.path.join(OUTPUT_DIR, combined_filename)  # Use OUTPUT_DIR from config

    torchaudio.save(combined_path, combined_audio, SAMPLE_RATE)

    print(f"Combined audio saved: {combined_path}")

    # Calculate final duration
    duration_seconds = combined_audio.shape[1] / SAMPLE_RATE

    return combined_path, int(duration_seconds)


# ============ Main Application Function ============

def generate_audio(text: str, output_name: Optional[str] = None, voice_type: str = 'normal'):
    """
    Generate audio from text using the selected TTS model and return (path, duration).
    This function now acts as a wrapper for the new tts_arabic core logic.
    """
    global tts_models, model_latents

    # Select Model and Latents based on voice_type
    if voice_type not in tts_models:
        print(f"Voice type '{voice_type}' not initialized. Defaulting to 'normal'.")
        voice_type = 'normal'

    if voice_type not in tts_models:
        print("Neither TTS model initialized.")
        return None, 0

    tts_model_instance = tts_models[voice_type]
    gpt_cond_latent, speaker_embedding = model_latents[voice_type]

    try:
        if not output_name:
            output_name = f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}_{voice_type}"

        print(f"Generating audio with '{voice_type}' voice (length: {len(text)} chars)...")

        # --- CALL THE NEW CORE FUNCTION ---
        output_path, duration = tts_arabic(
            prompt=text,
            model=tts_model_instance,
            gpt_cond_latent=gpt_cond_latent,
            speaker_embedding=speaker_embedding,
            output_name=output_name,
            temperature=0.7,
            speed=1.0,
            max_chunk_length=MAX_CHUNK_LENGTH,
            crossfade_ms=CROSSFADE_MS
        )
        # ----------------------------------

        print(f"✓ Duration: {duration} seconds")

        return output_path, duration

    except Exception as e:
        print(f"Error generating audio in tts_arabic: {e}")
        import traceback
        traceback.print_exc()
        return None, 0
