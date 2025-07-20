class StateManager:
    def __init__(self):
        self.conversation_history = []
        self.system_state = {
            "open_applications": [],
            "active_window": None
        }

    def add_message(self, role, content):
        """Role can be 'user' or 'assistant'."""
        self.conversation_history.append({"role": role, "content": content})

    def get_history(self):
        return self.conversation_history

    def clear_history(self):
        self.conversation_history = []