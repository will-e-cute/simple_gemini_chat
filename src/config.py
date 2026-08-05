from dataclasses import dataclass, field
import json
import os
from pathlib import Path
from typing import Dict
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Persona:
    key: str
    name: str
    description: str
    system_instruction: str


@dataclass
class AppConfig:
    api_key: str = field(
        default_factory=lambda: os.getenv("GEMINI_API_KEY", "").strip()
    )
    model_name: str = "gemini-2.5-flash"
    config_dir: Path = field(default_factory=lambda: Path("config"))
    personas_path: Path = field(init=False)

    def __post_init__(self) -> None:
        self.personas_path = self.config_dir / "personas.json"

    def load_personas(self) -> Dict[str, Persona]:
        if not self.personas_path.exists():
            raise FileNotFoundError(
                f"Fichier de personas introuvable: {self.personas_path}"
            )

        with open(self.personas_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return {
            key: Persona(
                key=key,
                name=val["name"],
                description=val["description"],
                system_instruction=val["system_instruction"],
            )
            for key, val in data.items()
        }