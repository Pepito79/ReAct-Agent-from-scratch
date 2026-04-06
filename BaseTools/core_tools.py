# BaseTools/core_tools.py

from datetime import datetime
import os
from pathlib import Path
import re

# ====================== CORE TOOLS FOR REACT AGENT ======================

def get_current_time() -> str:
    """
    Returns the current date and time in a readable format.
    
    Returns:
        str: Current time formatted as "It is HH:MM:SS - Day DD Month YYYY"
    """
    now = datetime.now()
    return now.strftime("It is %H:%M:%S - %A %d %B %Y")


def calculate(expression: str) -> str:
    """
    Evaluates a simple mathematical expression safely.
    
    Args:
        expression (str): Mathematical expression to evaluate (e.g., "25 * 18", "100 / 4 + 7")
    
    Returns:
        str: Result of the calculation or error message
    """
    try:
        allowed = set("0123456789+-*/().% ")
        if not all(c in allowed for c in expression):
            return "Error: Unauthorized characters in expression."
        return str(eval(expression))
    except Exception as e:
        return f"Calculation error: {str(e)}"


def list_files(directory: str = ".") -> str:
    """
    Lists all files and folders in a given directory.
    
    Args:
        directory (str): Path of the directory to list (default: current directory)
    
    Returns:
        str: Formatted list of folders and files
    """
    try:
        items = os.listdir(directory)
        files = [f for f in items if os.path.isfile(os.path.join(directory, f))]
        folders = [f for f in items if os.path.isdir(os.path.join(directory, f))]

        result = f"Contents of directory '{directory}':\n\n"
        if folders:
            result += "Folders:\n" + "\n".join([f"📁 {f}" for f in sorted(folders)]) + "\n\n"
        if files:
            result += "Files:\n" + "\n".join([f"📄 {f}" for f in sorted(files)])
        return result
    except Exception as e:
        return f"Error: Unable to list directory '{directory}' → {str(e)}"


def read_file(filepath: str) -> str:
    """
    Reads the full content of a text file.
    
    Args:
        filepath (str): Path to the file to read (relative or absolute)
    
    Returns:
        str: Content of the file or error message
    """
    try:
        if not os.path.exists(filepath):
            return f"Error: File '{filepath}' does not exist."
        
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        return f"Content of file '{filepath}':\n\n{content}"
    
    except Exception as e:
        return f"Error reading file '{filepath}': {str(e)}"


def grep_search(pattern: str, directory: str = ".", extension: str = None) -> str:
    """
    Searches for a pattern (text or regex) in files within a directory.
    
    Args:
        pattern (str): Text or regex pattern to search for
        directory (str): Directory to search in (default: current directory)
        extension (str, optional): Filter by file extension (e.g., ".py", ".txt")
    
    Returns:
        str: Search results formatted
    """
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
            return f"No results found for '{pattern}' in '{directory}'."

        output = f"🔍 Search results for '{pattern}' ({len(results)} found):\n\n"
        output += "\n".join(results[:40])
        if len(results) > 40:
            output += f"\n\n... and {len(results) - 40} more results."

        return output

    except Exception as e:
        return f"Search error: {str(e)}"


def write_python_file(filename: str, code: str) -> str:
    """
    Creates or overwrites a Python file with the given code.
    This is a sensitive action and should require human confirmation.
    
    Args:
        filename (str): Name of the file ('.py' extension will be added automatically if missing)
        code (str): Python code to write into the file
    
    Returns:
        str: Success or error message
    """
    try:
        if not filename.endswith('.py'):
            filename += '.py'

        os.makedirs("generated", exist_ok=True)
        filepath = f"generated/{filename}"

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)

        return f"✅ File '{filename}' successfully created in './generated/' folder."

    except Exception as e:
        return f"❌ Error writing file: {str(e)}"