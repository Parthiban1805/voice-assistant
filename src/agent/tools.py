from langchain_core.tools import tool
import subprocess
import os
from langchain_community.tools.tavily_search import TavilySearchResults
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.config import SENDER_EMAIL, SENDER_APP_PASSWORD

KNOWN_APPLICATIONS = {
    # We use the exact path you provided for Chrome.
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    
    # Notepad and Calculator are usually found automatically, but adding them is good practice.
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    
    # Add other applications you use frequently here.
    # Example for Visual Studio Code (you would need to find the real path):
    # "vscode": r"C:\Users\YourUser\AppData\Local\Programs\Microsoft VS Code\Code.exe"
}
# =====================================================================


@tool
def open_application(app_name: str) -> str:
    """
    Opens a specified application by looking up its full path from a known list.
    Handles simple names like 'chrome', 'notepad', etc.
    """
    app_name_lower = app_name.lower().replace('.exe', '') # Standardize the input name

    # Check if the requested app is in our known list
    if app_name_lower in KNOWN_APPLICATIONS:
        path_to_app = KNOWN_APPLICATIONS[app_name_lower]
        try:
            print(f"Opening '{app_name_lower}' using known path: {path_to_app}")
            subprocess.Popen([path_to_app])
            return f"Successfully started {app_name}."
        except FileNotFoundError:
            return f"Error: The path '{path_to_app}' for '{app_name}' was not found. Please check the path in tools.py."
        except Exception as e:
            return f"Error opening {app_name} with known path: {e}"
    else:
        # If not in our list, try to run it directly as a fallback
        try:
            print(f"'{app_name}' not in known list. Attempting to run directly...")
            subprocess.Popen([app_name])
            return f"Successfully started {app_name} (found in system PATH)."
        except Exception as e:
            return f"Error: Could not find '{app_name}' in the known applications list or in the system PATH. Error: {e}"

@tool
def search_web(query: str) -> str:
    """Searches the web for a given query using Tavily."""
    search = TavilySearchResults(max_results=3)
    results = search.invoke(query)
    return f"Web search results for '{query}':\n{results}"
@tool
def send_email(recipient: str, subject: str, body: str) -> str:
    """
    Sends an email to a specified recipient with a given subject and body.
    Uses the sender email configured in the system.
    """
    if not SENDER_EMAIL or not SENDER_APP_PASSWORD:
        return "Error: Sender email or app password is not configured. Please set it in the .env file."

    try:
        # Set up the email message
        message = MIMEMultipart()
        message["From"] = SENDER_EMAIL
        message["To"] = recipient
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        # Connect to Gmail's SMTP server and send the email
        # The 'with' statement ensures the connection is automatically closed
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
            server.send_message(message)
        
        return f"Email successfully sent to {recipient}."
    except Exception as e:
        print(f"Failed to send email: {e}")
        return f"Error: Failed to send email to {recipient}. The error was: {e}"


# You can add more tools here, e.g., for file system search (RAG) or pywinauto control
all_tools = [open_application, search_web,send_email]