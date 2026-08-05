from datetime import datetime
from pathlib import Path
from typing import Dict, List


class MarkdownExporter:
    @staticmethod
    def export(
        history: List[Dict[str, str]], persona_name: str, output_dir: str = "exports"
    ) -> Path:
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = out_path / f"chat_{timestamp}.md"

        lines = [
            f"# Discussion Gemini - Persona : {persona_name}",
            f"*Date : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n",
            "---",
            "",
        ]

        for msg in history:
            role = msg["role"]
            content = msg["content"]
            lines.append(
                f"### 👤 {role}" if role == "Utilisateur" else f"### 🤖 {role}"
            )
            lines.append(content)
            lines.append("\n---\n")

        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        return filename