from typing import Dict, List, Optional
from google import genai
from google.genai import types
from src.config import Persona


class GeminiService:
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash") -> None:
        self.api_key = api_key
        self.model_name = model_name
        self.client: Optional[genai.Client] = None
        self.chat_session = None
        self.current_persona: Optional[Persona] = None

        if self.api_key:
            self._init_client()

    def _init_client(self) -> None:
        self.client = genai.Client(api_key=self.api_key)

    def start_chat(self, persona: Persona) -> None:
        if not self.api_key:
            return

        if not self.client:
            self._init_client()

        self.current_persona = persona
        config = types.GenerateContentConfig(
            system_instruction=persona.system_instruction,
            temperature=0.7,
        )
        self.chat_session = self.client.chats.create(
            model=self.model_name, config=config
        )

    def send_message(self, message: str) -> str:
        if not self.api_key:
            return "[Erreur Configuration]: Clé GEMINI_API_KEY non renseignée dans le fichier .env"

        if not self.chat_session:
            return "[Erreur Session]: Aucune session active. Sélectionnez un persona."

        try:
            response = self.chat_session.send_message(message)
            return response.text or ""
        except Exception as e:
            return f"[Erreur API Gemini]: {str(e)}"

    def get_history(self) -> List[Dict[str, str]]:
        if not self.chat_session:
            return []
        history = []
        for turn in self.chat_session.get_history():
            role = "Utilisateur" if turn.role == "user" else "Gemini"
            parts_text = "".join([part.text for part in turn.parts if part.text])
            history.append({"role": role, "content": parts_text})
        return history