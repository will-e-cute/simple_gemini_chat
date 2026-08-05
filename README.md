# simple_gemini_chat
# 🤖 Client GUI Gemini Studio

Application desktop moderne et légère développée avec **CustomTkinter** et l'API **Google GenAI**. Elle permet d'interagir avec l'API Gemini via des personas (prompts systèmes personnalisables) et d'exporter les conversations au format Markdown.

---

## 🛠️ Architecture du Projet

```text
gemini_chat_gui/
├── config/
│   └── personas.json       # Fichier de configuration des agents (externe)
├── exports/                # Dossier généré automatiquement pour les exports .md
├── src/
│   ├── __init__.py
│   ├── config.py           # Chargement des variables & résolution des chemins
│   ├── export.py           # Génération des fichiers Markdown
│   └── gemini_client.py    # Interface avec le SDK google-genai
├── .env.example
├── app.spec                 # Configuration PyInstaller pour la compilation
├── main.py                 # Interface graphique et point d'entrée
└── requirements.txt
