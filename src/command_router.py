# src/command_router.py (Revised and Smarter)
import subprocess

def _control_volume(level):
    print(f"Setting volume to {level}")
    return f"Volume set to {level}."

FAST_PATH_COMMANDS = {
    "increase volume": lambda: _control_volume("up"),
    "decrease volume": lambda: _control_volume("down"),
    "mute": lambda: _control_volume("mute"),
    "open calculator": lambda: subprocess.Popen(['calc']) and "Opening calculator."
}

def route_command(text: str):
    """
    Intelligently routes the user's command. It checks for the complex WhatsApp
    "Flirt Mode" first, then simple commands, before falling back to the main AI agent.
    """
    text_lower = text.lower()

    # --- NEW, MORE ROBUST LOGIC FOR WHATSAPP FLIRT MODE ---
    # This is the most specific and complex command, so we check for it first.
    chat_keywords = ["flirt", "chat", "message", "talk to"]
    
    # Check if the intent involves BOTH WhatsApp AND a chat-related action.
    if 'whatsapp' in text_lower and any(keyword in text_lower for keyword in chat_keywords):
        # The intent is confirmed. Now, extract the contact name.
        # The name usually follows prepositions like "with" or "to".
        try:
            name_preposition = ""
            if "with " in text_lower:
                name_preposition = "with "
            elif "to " in text_lower:
                name_preposition = "to "
            
            if name_preposition:
                contact_name = text_lower.split(name_preposition, 1)[1].title()
                contact_name = contact_name.strip().strip('"\'')
                print(f"Flirt Mode triggered for contact: {contact_name}")
                return ("FLIRT_MODE", contact_name)
        except IndexError:
            # This happens if the command is "flirt on whatsapp" without a name.
            # We can let the main agent handle this ambiguity.
            pass

    # --- Existing logic for simple, fast commands ---
    for command, func in FAST_PATH_COMMANDS.items():
        if command in text_lower:
            return func()
    
    # --- Fallback to the main AI agent for all other commands ---
    # If the command wasn't a special mode or a simple command, it's a job for the General Agent.
    print("Command not routed to a special mode. Passing to main agent.")
    return "AGENT"