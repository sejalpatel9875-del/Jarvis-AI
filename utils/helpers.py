import re
import sys

def configure_encoding():
    """Ensures UTF-8 encoding support on Windows terminal."""
    if sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass
    if sys.stderr.encoding != 'utf-8':
        try:
            sys.stderr.reconfigure(encoding='utf-8')
        except Exception:
            pass

def clean_speech_phonetics(text: str) -> str:
    """Corrects common Indian English STT misrecognitions phonetically."""
    if not text:
        return ""
    cleaned = text.strip().lower()
    
    gpt_patterns = [
        (r'\b4g\s*ppt\b', 'chatgpt'),
        (r'\b4g\s*pt\b', 'chatgpt'),
        (r'\b4g\s*app\b', 'chatgpt'),
        (r'\b4g\s*p\b', 'chatgpt'),
        (r'\b4g\b', 'chatgpt'),
        (r'\bchat\s*ppt\b', 'chatgpt'),
        (r'\bcat\s*gpt\b', 'chatgpt'),
        (r'\bchar\s*gpt\b', 'chatgpt'),
        (r'\bchachi\s*pt\b', 'chatgpt'),
    ]
    for pattern, replacement in gpt_patterns:
        cleaned = re.sub(pattern, replacement, cleaned)
        
    return cleaned
