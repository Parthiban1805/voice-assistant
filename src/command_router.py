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

def route_command(text: str):
    """Checks for a fast-path command first, otherwise returns 'AGENT'."""
    for command, func in FAST_PATH_COMMANDS.items():
        if command in text.lower():
            return func() # Execute the simple function
    
    # If no simple command is found, it needs the agent
    return "AGENT"