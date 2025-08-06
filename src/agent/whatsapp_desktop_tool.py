# src/agent/whatsapp_desktop_tool.py (Revised with Correct Path Handling)
from pywinauto.application import Application
from pywinauto.findwindows import ElementNotFoundError
import time
import re # Import the regular expression library

# Global variable to store the last seen message
last_seen_message = ""

def start_whatsapp_desktop_session(contact_name: str):
    """
    Starts or connects to the WhatsApp desktop app and navigates to a specific chat.
    """
    print(f"Starting WhatsApp Desktop session for contact: '{contact_name}'")
    try:
        app = Application(backend="uia").connect(title_re="WhatsApp.*", timeout=10)
        main_window = app.window(title_re="WhatsApp.*")
        print("Connected to existing WhatsApp window.")
    except ElementNotFoundError:
        print("WhatsApp not found running. Starting the application...")
        
        # ========================== THIS IS THE FIX ==========================
        # You MUST replace the placeholder path below with the real path you found.
        # Right-click your WhatsApp shortcut -> Properties -> Target
        try:
            whatsapp_path = r"C:\Users\sunda\AppData\Local\WhatsApp\WhatsApp.exe" # <-- EDIT THIS LINE
            app = Application(backend="uia").start(whatsapp_path)
            main_window = app.window(title_re="WhatsApp.*")
            main_window.wait("ready", timeout=30)
            print("WhatsApp started successfully.")
        except Exception as e:
            print(f"FATAL ERROR: Could not start WhatsApp from the specified path. Please check the path in whatsapp_desktop_tool.py. Error: {e}")
            return None
        # =====================================================================

    try:
        # --- Find and click the chat ---
        search_box = main_window.child_window(title="Search or start new chat", control_type="Edit")
        search_box.wait('visible', timeout=20)
        search_box.set_text(contact_name)
        time.sleep(2)

        # FIX: Use a regular expression search to handle special characters like '&' safely
        contact_item = main_window.child_window(title_re=f".*{re.escape(contact_name)}.*", control_type="ListItem")
        contact_item.wait('visible', timeout=10)
        contact_item.click_input()
        print(f"Successfully opened chat with {contact_name}.")
        return main_window

    except Exception as e:
        print(f"Error navigating to contact: {e}")
        return None

def send_whatsapp_message(main_window, message: str):
    """Sends a message to the currently active chat using pywinauto."""
    try:
        message_box = main_window.child_window(title="Type a message", control_type="Edit")
        message_box.wait('ready', timeout=10)
        message_box.type_keys(message, with_spaces=True, with_newlines=False)
        
        send_button = main_window.child_window(title="Send", control_type="Button")
        send_button.click()
        print(f"Sent message: '{message}'")
        return True
    except Exception as e:
        print(f"Error sending message: {e}")
        return False

def read_latest_reply(main_window) -> str | None:
    """Reads the latest message. NOTE: This is brittle and may require inspection tools."""
    global last_seen_message
    try:
        # This is a guess. You may need Inspect.exe to find the right control.
        chat_pane = main_window.child_window(control_type="List", found_index=0)
        messages = chat_pane.children(control_type="ListItem")
        
        if not messages: return None

        latest_message_text = messages[-1].window_text()

        if latest_message_text and latest_message_text != last_seen_message:
            last_seen_message = latest_message_text
            print(f"Read new reply: '{latest_message_text}'")
            return latest_message_text
        else:
            return None
    except Exception:
        return None