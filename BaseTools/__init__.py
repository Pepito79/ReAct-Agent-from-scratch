# BaseTools/core_tools.py

from datetime import datetime
import os
from pathlib import Path
import re

# ====================== TOOLS DE BASE INDISPENSABLES ======================

def get_current_time() -> str:
    """Retourne l'heure et la date actuelle de manière lisible"""
    now = datetime.now()
    return now.strftime("Il est %H:%M:%S - %A %d %B %Y")


def calculate(expression: str) -> str:
    """Évalue une expression mathématique simple de façon sécurisée"""
    try:
        allowed_chars = set("0123456789+-*/().% ")
        if not all(c in allowed_chars for c in expression):
            return "Erreur : Caractères non autorisés dans l'expression."
        return str(eval(expression))
    except Exception as e:
        return f"Erreur de calcul : {str(e)}"


def list_files(directory: str = ".") -> str:
    """Liste les fichiers et dossiers dans un répertoire donné"""
    try:
        items = os.listdir(directory)
        files = [f for f in items if os.path.isfile(os.path.join(directory, f))]
        folders = [f for f in items if os.path.isdir(os.path.join(directory, f))]

        result = f"Contenu du dossier '{directory}' :\n\n"
        if folders:
            result += "Dossiers :\n" + "\n".join([f"📁 {f}" for f in sorted(folders)]) + "\n\n"
        if files:
            result += "Fichiers :\n" + "\n".join([f"📄 {f}" for f in sorted(files)])
        return result
    except Exception as e:
        return f"Erreur : Impossible de lister le dossier '{directory}' : {str(e)}"


def grep_search(pattern: str, directory: str = ".", extension: str = None) -> str:
    """Cherche un motif (texte ou regex) dans les fichiers d'un dossier"""
    try:
        results = []
        search_path = Path(directory)

        for file_path in search_path.rglob("*"):
            if file_path.is_file():
                if extension and not str(file_path).endswith(extension):
                    continue
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        for line_num, line in enumerate(f, 1):
                            if re.search(pattern, line, re.IGNORECASE):
                                snippet = line.strip()[:150]
                                results.append(f"{file_path}:{line_num}: {snippet}")
                except:
                    continue

        if not results:
            return f"Aucun résultat trouvé pour '{pattern}' dans '{directory}'."

        output = f"🔍 Résultats de recherche pour '{pattern}' ({len(results)} trouvés) :\n\n"
        output += "\n".join(results[:40])
        if len(results) > 40:
            output += f"\n\n... et {len(results) - 40} autres résultats."

        return output

    except Exception as e:
        return f"Erreur lors de la recherche : {str(e)}"


def write_python_file(filename: str, code: str) -> str:
    """Crée ou écris du code Python dans un fichier (action sensible)"""
    try:
        if not filename.endswith('.py'):
            filename += '.py'

        # Sécurité : on force le dossier "generated"
        os.makedirs("generated", exist_ok=True)
        filepath = f"generated/{filename}"

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)

        return f"✅ Fichier '{filename}' créé avec succès dans le dossier './generated/'."

    except Exception as e:
        return f"❌ Erreur lors de l'écriture du fichier : {str(e)}"