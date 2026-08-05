import threading
import customtkinter as ctk
from src.config import AppConfig, Persona
from src.export import MarkdownExporter
from src.gemini_client import GeminiService

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class GeminiChatGUI(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        self.config = AppConfig()
        self.personas = self.config.load_personas()
        self.service = GeminiService(api_key=self.config.api_key)
        self.current_persona: Persona = list(self.personas.values())[0]

        self.title("Gemini Studio Client")
        self.geometry("900x650")
        self.minsize(700, 500)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_chat_area()
        self._init_app_state()

    def _build_sidebar(self) -> None:
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.sidebar.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(
            self.sidebar, text="Gemini Agent App", font=ctk.CTkFont(size=18, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.persona_label = ctk.CTkLabel(
            self.sidebar, text="Sélection du Persona:", anchor="w"
        )
        self.persona_label.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="w")

        persona_names = [p.name for p in self.personas.values()]
        self.persona_dropdown = ctk.CTkOptionMenu(
            self.sidebar, values=persona_names, command=self._on_persona_change
        )
        self.persona_dropdown.grid(row=2, column=0, padx=20, pady=(5, 20), sticky="ew")

        self.save_button = ctk.CTkButton(
            self.sidebar, text="💾 Sauvegarder (MD)", command=self._save_chat
        )
        self.save_button.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        self.status_label = ctk.CTkLabel(
            self.sidebar, text="", font=ctk.CTkFont(size=11), wraplength=180
        )
        self.status_label.grid(row=5, column=0, padx=20, pady=20, sticky="ew")

    def _build_chat_area(self) -> None:
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        self.chat_display = ctk.CTkTextbox(
            self.main_frame, font=ctk.CTkFont(size=13), wrap="word"
        )
        self.chat_display.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="nsew")

        self.input_frame = ctk.CTkFrame(self.main_frame)
        self.input_frame.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.entry = ctk.CTkEntry(
            self.input_frame, placeholder_text="Tapez votre message..."
        )
        self.entry.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="ew")
        self.entry.bind("<Return>", lambda e: self._send_message())

        self.send_button = ctk.CTkButton(
            self.input_frame, text="Envoyer", width=100, command=self._send_message
        )
        self.send_button.grid(row=0, column=1, padx=(5, 10), pady=10)

    def _init_app_state(self) -> None:
        if not self.config.api_key:
            self._append_system_msg(
                "ATTENTION: GEMINI_API_KEY manquante dans le .env\n"
                "Renseignez votre clé pour utiliser l'application."
            )
            self.status_label.configure(text="Clé API manquante", text_color="red")
        else:
            self.service.start_chat(self.current_persona)
            self._append_system_msg(f"Agent actif : {self.current_persona.name}")
            self.status_label.configure(text="Prêt", text_color="green")

    def _on_persona_change(self, selected_name: str) -> None:
        for persona in self.personas.values():
            if persona.name == selected_name:
                self.current_persona = persona
                break

        self.service.start_chat(self.current_persona)
        self._append_system_msg(f"Changement d'agent -> {self.current_persona.name}")

    def _send_message(self) -> None:
        user_text = self.entry.get().strip()
        if not user_text:
            return

        self.entry.delete(0, "end")
        self._append_user_msg(user_text)

        self.send_button.configure(state="disabled")
        self.status_label.configure(text="Gemini réfléchit...", text_color="yellow")

        threading.Thread(
            target=self._async_send_worker, args=(user_text,), daemon=True
        ).start()

    def _async_send_worker(self, message: str) -> None:
        response_text = self.service.send_message(message)
        self.after(0, self._handle_response, response_text)

    def _handle_response(self, response_text: str) -> None:
        self._append_agent_msg(self.current_persona.name, response_text)
        self.send_button.configure(state="normal")
        self.status_label.configure(text="Prêt", text_color="green")

    def _save_chat(self) -> None:
        history = self.service.get_history()
        if not history:
            self.status_label.configure(text="Rien à exporter", text_color="orange")
            return

        filepath = MarkdownExporter.export(history, self.current_persona.name)
        self._append_system_msg(f"Export réussi : {filepath}")
        self.status_label.configure(text="Discussion sauvegardée", text_color="green")

    def _append_user_msg(self, msg: str) -> None:
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", f"\n👤 Vous:\n{msg}\n")
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")

    def _append_agent_msg(self, persona_name: str, msg: str) -> None:
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", f"\n🤖 Gemini [{persona_name}]:\n{msg}\n")
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")

    def _append_system_msg(self, msg: str) -> None:
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", f"\n⚙️ System: {msg}\n")
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")


if __name__ == "__main__":
    app = GeminiChatGUI()
    app.mainloop()