from langchain_core.tools import tool
import subprocess
import os
from langchain_community.tools.tavily_search import TavilySearchResults

@tool
def open_application(app_name: str) -> str:
    """Opens a specified application. For example, 'notepad.exe', 'chrome', 'calc'."""
    try:
        if os.name == 'nt': # For Windows
            subprocess.Popen([app_name])
        elif os.name == 'posix': # For macOS/Linux
            subprocess.Popen(['open', '-a', app_name] if os.uname().sysname == 'Darwin' else [app_name])
        return f"Successfully started {app_name}."
    except Exception as e:
        return f"Error opening {app_name}: {e}"

@tool
def search_web(query: str) -> str:
    """Searches the web for a given query using Tavily."""
    search = TavilySearchResults(max_results=3)
    results = search.invoke(query)
    return f"Web search results for '{query}':\n{results}"

# You can add more tools here, e.g., for file system search (RAG) or pywinauto control
all_tools = [open_application, search_web]