import subprocess

def _control_volume(level):
    # This is a placeholder. Real implementation is OS-specific.
    print(f"Setting volume to {level}")
    return f"Volume set to {level}."

# Simple, fast commands that don't need an LLM
FAST_PATH_COMMANDS = {
    "increase volume": lambda: _control_volume("up"),
    "decrease volume": lambda: _control_volume("down"),
    "mute": lambda: _control_volume("mute"),
    "open calculator": lambda: subprocess.Popen(['calc']) and "Opening calculator."
}

# src/command_router.py

# ... (keep existing code) ...

def route_command(text: str):
    """
    Intelligently routes the user's command. It checks for special modes like
    "Flirt Mode" first, then simple commands, before falling back to the main AI agent.
    """
    text_lower = text.lower()

    # --- NEW, MORE FLEXIBLE LOGIC FOR FLIRT MODE ---
    # Define the phrases that trigger this special mode.
    flirt_triggers = ["flirt with ", "chat with ", "start a chat with "]
    
    for trigger in flirt_triggers:
        if trigger in text_lower:
            # Extract the name by splitting the text right after the trigger phrase.
            # We take the second part [1] of the split.
            try:
                contact_name = text_lower.split(trigger, 1)[1].title()
                print(f"Flirt Mode triggered for contact: {contact_name}")
                return ("FLIRT_MODE", contact_name)
            except IndexError:
                # This happens if the command ends with the trigger, e.g., "start a chat with"
                # The agent will handle asking for the name.
                pass 

    # --- Existing logic for simple, fast commands ---
    for command, func in FAST_PATH_COMMANDS.items():
        if command in text_lower:
            return func()
    
    # --- Fallback to the main AI agent for all other commands ---
    print("Command not routed to a special mode. Passing to main agent.")
    return "AGENT"