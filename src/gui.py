import tkinter as tk
import threading

class StatusGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TAM-VA Status")
        self.root.geometry("300x100")
        self.status_label = tk.Label(self.root, text="Initializing...", font=("Helvetica", 12), wraplength=280)
        self.status_label.pack(pady=20, padx=10)
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.is_running = True

    def update_status(self, text, color="black"):
        def _update():
            self.status_label.config(text=text, fg=color)
        self.root.after(0, _update)

    def run(self):
        self.root.mainloop()

    def _on_closing(self):
        self.is_running = False
        self.root.destroy()