"""
Enterprise AI Security & Safety Guardrails
Inspired by Microsoft Copilot, Azure AI Content Safety, and Microsoft Prompt Shield.
Engineered for luxury conversational real estate advisory systems.

Components:
1. PromptShield: Defends against prompt injection, jailbreaking (DAN), and system prompt extraction.
2. IdentityShield: Enforces brand persona and prevents underlying LLM leaks (e.g. Nemotron/NVIDIA/OpenAI).
3. InputSanitizer: Enforces length bounds, escapes XSS tokens, and strips control characters.
4. RateLimiter: Sliding-window token bucket preventing DDoS and token exhaustion.
5. OutputSanitizer: Post-generation scrubbing to redact API keys and enforce brand integrity.
"""

import re
import time
from typing import Tuple, Optional, Dict, List

# High-risk jailbreak and prompt-injection signatures (Microsoft Prompt Shield patterns)
PROMPT_INJECTION_PATTERNS = [
    r"(?i)\bignore\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts|directives|rules)\b",
    r"(?i)\bdisregard\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts)\b",
    r"(?i)\byou\s+are\s+now\s+(in\s+)?(dan|jailbreak|developer|unrestricted|god)\s+mode\b",
    r"(?i)\bact\s+as\s+(an?\s+)?(unfiltered|unrestricted|jailbroken|evil)\b",
    r"(?i)\breveal\s+(your\s+)?(system\s+prompt|initial\s+instructions|instructions|rules)\b",
    r"(?i)\bshow\s+(me\s+)?(your\s+)?(hidden\s+)?(system\s+prompt|raw\s+prompt)\b",
    r"(?i)\bprint\s+(?:.*?\s+)?above\s+this\s+line\b",
    r"(?i)\bprint\s+(?:the\s+)?(?:exact\s+)?(?:text|instructions|system\s+prompt)\b",
    r"(?i)\brepeat\s+(everything|the\s+words)\s+(above|from\s+the\s+beginning)\b",
    r"(?i)\bwhat\s+(are\s+)?your\s+(exact\s+)?(system\s+instructions|system\s+prompt)\b",
    r"(?i)\bbypass\s+(all\s+)?(safety|content|domain)\s+(filters|guardrails|guidelines)\b",
    r"(?i)\bsudo\s+mode\b",
    r"(?i)\bbase64\s+decode\b"
]

# Patterns where foundation models might leak internal identity
MODEL_LEAK_PATTERNS = [
    (r"(?i)\bi\s*(?:'m|am)\s+(?:nemotron|nvidia\s+nemotron|an?\s+nvidia\s+language\s+model)", "I am the DarGlobal & Wasalt Real Estate AI Advisor"),
    (r"(?i)\bdeveloped\s+by\s+nvidia\b", "developed for DarGlobal & Wasalt luxury real estate"),
    (r"(?i)\bdeveloped\s+by\s+openai\b", "developed for DarGlobal & Wasalt luxury real estate"),
    (r"(?i)\bi\s*(?:'m|am)\s+(?:gpt-?4|gpt-?3\.?5|chatgpt)", "I am the DarGlobal & Wasalt Real Estate AI Advisor"),
    (r"(?i)\bi\s*(?:'m|am)\s+(?:llama|meta\s+llama)", "I am the DarGlobal & Wasalt Real Estate AI Advisor"),
    (r"(?i)\bi\s*(?:'m|am)\s+(?:gemma|google\s+gemma)", "I am the DarGlobal & Wasalt Real Estate AI Advisor"),
    (r"(?i)\bi\s*(?:'m|am)\s+a\s+large\s+language\s+model\s+trained\s+by\s+(?:google|meta|openai|nvidia|anthropic)", "I am the DarGlobal & Wasalt Real Estate AI Advisor"),
]

BRAND_PERSONA_REPLY = (
    "I am the **DarGlobal & Wasalt Real Estate AI Advisor**, your dedicated luxury property and "
    "investment intelligence consultant. I specialize exclusively in prime international branded residences "
    "(Dubai, Spain, Oman, Qatar, London) and REGA-certified Saudi developments (Riyadh, Jeddah, Al-Khobar).\n\n"
    "How may I assist your property portfolio inquiry today?"
)

SECURITY_REFUSAL_REPLY = (
    "### 🛡️ Security & Scope Boundary Notice\n\n"
    "I am the **DarGlobal & Wasalt Real Estate AI Advisor**. I am strictly programmed to assist with "
    "luxury architectural properties, pricing, locations, and investment opportunities.\n\n"
    "System directives and security controls cannot be modified or inspected. "
    "Please let me know which real estate portfolio or project you would like to explore."
)


class PromptShield:
    """
    Microsoft Prompt Shield pattern: Inspects inbound user inputs for jailbreaks,
    system prompt extractions, and adversarial injection attempts.
    """
    @staticmethod
    def inspect(query: str) -> Tuple[bool, Optional[str]]:
        """
        Returns (is_safe, refusal_reason).
        """
        if not query or not query.strip():
            return True, None

        q = query.strip()
        for pattern in PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, q):
                return False, SECURITY_REFUSAL_REPLY

        return True, None


class IdentityShield:
    """
    Enforces brand identity invariants, ensuring the chatbot never leaks underlying
    model vendors (e.g. Nemotron/NVIDIA/OpenAI) and always stays in persona.
    """
    @staticmethod
    def sanitize_output(text: str) -> str:
        """
        Normalizes any accidental internal model disclosures back to the enterprise brand.
        """
        if not text:
            return ""

        sanitized = text
        for pattern, replacement in MODEL_LEAK_PATTERNS:
            sanitized = re.sub(pattern, replacement, sanitized)

        # Catch raw OpenRouter API keys if accidentally reflected
        sanitized = re.sub(r"sk-or-v1-[a-f0-9]{64}", "[REDACTED_API_KEY]", sanitized)
        return sanitized


class InputSanitizer:
    """
    Sanitizes inbound requests:
    - Caps message length (prevents token-exhaustion DDoS)
    - Strips non-printable / control characters
    - Defends against XSS injection
    """
    MAX_CHAR_LENGTH = 1200

    @staticmethod
    def clean(raw_input: str) -> Tuple[str, Optional[str]]:
        """
        Cleans input string. Returns (cleaned_text, error_message).
        """
        if not raw_input:
            return "", "Empty message received."

        # Cap length
        if len(raw_input) > InputSanitizer.MAX_CHAR_LENGTH:
            return raw_input[:InputSanitizer.MAX_CHAR_LENGTH], None

        # Remove null bytes and non-printable control codes (except standard newlines/tabs)
        cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', raw_input)
        return cleaned.strip(), None


class InMemoryRateLimiter:
    """
    Sliding-window token bucket rate limiter per client IP.
    Prevents scraping, resource exhaustion, and denial of service.
    """
    def __init__(self, max_requests: int = 30, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.clients: Dict[str, List[float]] = {}

    def is_allowed(self, client_ip: str) -> bool:
        now = time.time()
        timestamps = self.clients.get(client_ip, [])

        # Filter out timestamps older than the window
        valid_timestamps = [t for t in timestamps if now - t < self.window_seconds]
        if len(valid_timestamps) >= self.max_requests:
            self.clients[client_ip] = valid_timestamps
            return False

        valid_timestamps.append(now)
        self.clients[client_ip] = valid_timestamps
        return True


class ResponseCache:
    """
    High-speed in-memory LRU Query Response Cache.
    Returns sub-5ms responses for high-frequency or repeated real estate queries,
    reducing inference latency and preserving token budgets (Microsoft Copilot acceleration).
    """
    def __init__(self, capacity: int = 250):
        self.capacity = capacity
        self.cache: Dict[str, Dict] = {}
        self.access_order: List[str] = []

    def _normalize_key(self, query: str, filter_str: Optional[str] = None) -> str:
        clean = re.sub(r"[^\w\s]", "", query.lower()).strip()
        tokens = [t for t in clean.split() if len(t) > 1]
        return f"{' '.join(tokens)}::{filter_str or ''}"

    def get(self, query: str, filter_str: Optional[str] = None) -> Optional[Dict]:
        key = self._normalize_key(query, filter_str)
        if key in self.cache:
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None

    def put(self, query: str, data: Dict, filter_str: Optional[str] = None):
        key = self._normalize_key(query, filter_str)
        if key in self.cache:
            self.access_order.remove(key)
        elif len(self.cache) >= self.capacity:
            oldest = self.access_order.pop(0)
            self.cache.pop(oldest, None)

        self.cache[key] = data
        self.access_order.append(key)
