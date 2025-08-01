from langchain_core.tools import tool
import subprocess
import os
from langchain_community.tools.tavily_search import TavilySearchResults
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.config import SENDER_EMAIL, SENDER_APP_PASSWORD

KNOWN_APPLICATIONS = {
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
}

# ========================== THIS IS THE NEW PART ==========================
# Create a dictionary to map easy-to-say profile names to the internal
# directory names you found in Step 1.
CHROME_PROFILES = {
    # You MUST replace these with the real values you found from chrome://version
    "Profile 94": "Default",  # Assuming this is your default profile
    "Profile 106": "Profile 2", # Example for another profile
    
}
DEFAULT_CHROME_PROFILE = "Profile 94" # The key from the dictionary above to use as a default
# ==========================================================================


@tool
def open_application(app_name: str, profile_name: str = None) -> str:
    """
    Opens a specified application. For Chrome, you can optionally specify a 
    'profile_name' (e.g., 'parthiban s', 'work'). If no profile is given for
    Chrome, a default one will be used.
    """
    app_name_lower = app_name.lower().replace('.exe', '')

    # --- SPECIAL LOGIC FOR CHROME ---
    if app_name_lower == 'chrome':
        path_to_chrome = KNOWN_APPLICATIONS.get('chrome')
        if not path_to_chrome:
            return "Error: The path for Chrome is not configured in tools.py."

        profile_to_use = None
        if profile_name:
            profile_to_use = profile_name.lower()
        else:
            profile_to_use = DEFAULT_CHROME_PROFILE

        internal_profile_dir = CHROME_PROFILES.get(profile_to_use)

        if not internal_profile_dir:
            return f"Error: Profile '{profile_to_use}' is not defined in the CHROME_PROFILES dictionary in tools.py."
        
        try:
            command = [path_to_chrome, f'--profile-directory={internal_profile_dir}']
            print(f"Opening Chrome with command: {command}")
            subprocess.Popen(command)
            return f"Successfully started Chrome with profile '{profile_to_use}'."
        except Exception as e:
            return f"Error opening Chrome with profile: {e}"
    
    # --- FALLBACK LOGIC FOR ALL OTHER APPLICATIONS ---
    elif app_name_lower in KNOWN_APPLICATIONS:
        path_to_app = KNOWN_APPLICATIONS[app_name_lower]
        try:
            print(f"Opening '{app_name_lower}' using known path: {path_to_app}")
            subprocess.Popen([path_to_app])
            return f"Successfully started {app_name}."
        except Exception as e:
            return f"Error opening {app_name} with known path: {e}"
    else:
        return f"Error: Could not find '{app_name}'. It is not in the known applications list."

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