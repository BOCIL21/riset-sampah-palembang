import json
import urllib.request
from typing import Any, Dict, Optional
from config.settings import Settings


class LLMClient:
    """
    Wrapper modular untuk memanggil Large Language Model (Gemini / OpenAI) via REST API.
    Bebas konflik protobuf di Google Colab & kompatibel dengan Python 3.10 - 3.13+.
    Dilengkapi mode fallback otomatis agar sistem tetap dapat diuji tanpa API key aktif.
    """

    def __init__(self, provider: Optional[str] = None) -> None:
        self.provider = (provider or Settings.AI_PROVIDER).lower()
        self.model_name = Settings.AI_MODEL_NAME

    def is_live_ai_ready(self) -> bool:
        """Memeriksa apakah kredensial AI live sudah siap digunakan."""
        status = Settings.credential_status()
        if self.provider == "gemini":
            return status["gemini_api_key_ready"]
        if self.provider == "openai":
            return status["openai_api_key_ready"]
        return False

    def generate_json(self, system_prompt: str, user_text: str, fallback_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Meminta output terstruktur JSON dari LLM (Gemini / OpenAI).
        Jika API key belum diisi atau mode offline_fallback, mengembalikan fallback_data.
        """
        if not self.is_live_ai_ready():
            return fallback_data

        try:
            if self.provider == "gemini":
                return self._call_gemini_rest(system_prompt, user_text)
            if self.provider == "openai":
                return self._call_openai_rest(system_prompt, user_text)
        except Exception as exc:
            fallback_copy = dict(fallback_data)
            fallback_copy["ai_warning"] = f"Fallback aktif karena error API: {exc}"
            return fallback_copy

        return fallback_data

    def _call_gemini_rest(self, system_prompt: str, user_text: str) -> Dict[str, Any]:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model_name}:generateContent?key={Settings.GEMINI_API_KEY}"
        )
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{system_prompt}\n\nTeks Input:\n{user_text}"}
                    ]
                }
            ],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.1,
            },
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        text_out = body["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(text_out)

    def _call_openai_rest(self, system_prompt: str, user_text: str) -> Dict[str, Any]:
        url = "https://api.openai.com/v1/chat/completions"
        payload = {
            "model": self.model_name,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text},
            ],
            "temperature": 0.1,
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {Settings.OPENAI_API_KEY}",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        content = body["choices"][0]["message"]["content"]
        return json.loads(content)
