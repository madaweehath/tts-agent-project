# tts_service.py
import os
import torch
import torchaudio
from datetime import datetime
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
from config import CHECKPOINT_PATH, CONFIG_PATH, TOKENIZER_PATH, SPEAKER_REFERENCE, OUTPUT_DIR
import uuid
from typing import Optional

tts_model = None
gpt_cond_latent = None
speaker_embedding = None

def initialize_tts():
    """Initialize TTS model on startup"""
    global tts_model, gpt_cond_latent, speaker_embedding
    
    try:
        print("🎤 Loading TTS model...")
        config = XttsConfig()
        config.load_json(CONFIG_PATH)
        
        tts_model = Xtts.init_from_config(config)
        tts_model.load_checkpoint(
            config,
            checkpoint_path=CHECKPOINT_PATH,
            vocab_path=TOKENIZER_PATH,
            use_deepspeed=False
        )
        
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        tts_model.to(device)
        tts_model.eval()
        
        print("🎤 Computing speaker latents...")
        gpt_cond_latent, speaker_embedding = tts_model.get_conditioning_latents(
            audio_path=[SPEAKER_REFERENCE]
        )
        
        print(f"✓ TTS model loaded on {device}")
        return True
    except Exception as e:
        print(f"✗ Error loading TTS model: {e}")
        import traceback
        traceback.print_exc()
        return False
# def generate_audio(text: str, output_name: Optional[str] = None) -> Optional[str]:

def generate_audio(text: str, output_name: Optional[str] = None):
    """Generate audio from text using TTS model and return (path, duration)"""
    if not tts_model:
        print("❌ TTS model not initialized")
        return None, 0
    
    try:
        print(f"🎙️  Generating audio for text (length: {len(text)} chars)...")
        
        out = tts_model.inference(
            text=text,
            language="ar",
            gpt_cond_latent=gpt_cond_latent,
            speaker_embedding=speaker_embedding,
            temperature=0.7,
            speed=1.0,
            enable_text_splitting=True
        )
        
        if not output_name:
            output_name = f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        output_path = os.path.join(OUTPUT_DIR, f"{output_name}.wav")
        
        # Get audio tensor
        audio_tensor = torch.tensor(out["wav"]).unsqueeze(0)
        
        # Calculate duration from tensor
        sample_rate = 24000  # XTTS uses 24000 Hz
        num_samples = audio_tensor.shape[1]
        duration_seconds = num_samples / sample_rate
        
        # Save audio
        torchaudio.save(output_path, audio_tensor, sample_rate)
        print(f"✓ Audio saved: {output_path}")
        print(f"✓ Duration: {int(duration_seconds)} seconds")
        
        return output_path, int(duration_seconds)
        
    except Exception as e:
        print(f"❌ Error generating audio: {e}")
        import traceback
        traceback.print_exc()
        return None, 0

# import os
# import torch
# import torchaudio
# import uuid
# from typing import Optional
# from datetime import datetime
# import traceback
# from TTS.tts.configs.xtts_config import XttsConfig
# from TTS.tts.models.xtts import Xtts
# from config import CHECKPOINT_PATH, CONFIG_PATH, TOKENIZER_PATH, SPEAKER_REFERENCE, OUTPUT_DIR

# # ============ TTS Model Globals ============
# tts_model = None
# gpt_cond_latent = None
# speaker_embedding = None

# def initialize_tts():
#     """Initialize TTS model on startup"""
#     global tts_model, gpt_cond_latent, speaker_embedding
    
#     # ... (body of initialize_tts function remains the same)
#     try:
#         print("🎤 Loading TTS model...")
#         config = XttsConfig()
#         config.load_json(CONFIG_PATH)
        
#         tts_model = Xtts.init_from_config(config)
#         tts_model.load_checkpoint(
#             config,
#             checkpoint_path=CHECKPOINT_PATH,
#             vocab_path=TOKENIZER_PATH,
#             use_deepspeed=False
#         )
        
#         device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#         tts_model.to(device)
#         tts_model.eval()
        
#         print("🎤 Computing speaker latents...")
#         gpt_cond_latent, speaker_embedding = tts_model.get_conditioning_latents(
#             audio_path=[SPEAKER_REFERENCE]
#         )
        
#         print(f"✓ TTS model loaded on {device}")
#         return True
#     except Exception as e:
#         print(f"✗ Error loading TTS model: {e}")
#         traceback.print_exc()
#         return False

# def generate_audio(text: str, output_name: Optional[str] = None) -> Optional[str]:
#     """Generate audio from text using TTS model"""
#     # Removed global declaration and now using the global variables loaded in initialize_tts
#     if not tts_model:
#         print("❌ TTS model not initialized")
#         return None
        
#     # ... (body of generate_audio function remains the same)
#     try:
#         print(f"🎙️  Generating audio for text (length: {len(text)} chars)...")
        
#         out = tts_model.inference(
#             text=text,
#             language="ar",
#             gpt_cond_latent=gpt_cond_latent,
#             speaker_embedding=speaker_embedding,
#             temperature=0.7,
#             speed=1.0,
#             enable_text_splitting=True
#         )
        
#         if not output_name:
#             output_name = f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
#         output_path = os.path.join(OUTPUT_DIR, f"{output_name}.wav")
        
#         torchaudio.save(output_path, torch.tensor(out["wav"]).unsqueeze(0), 24000)
#         print(f"✓ Audio saved: {output_path}")
        
#         return output_path
        
#     except Exception as e:
#         print(f"❌ Error generating audio: {e}")
#         traceback.print_exc()
#         return None