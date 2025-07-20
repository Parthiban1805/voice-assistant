# main.py (Corrected threading model)
import threading
import time
from src.gui import StatusGUI
from src.wake_word import WakeWordDetector
from src.speech_to_text import SpeechToText
from src.local_tts import LocalTTS
from src.command_router import route_command
from src.agent.agent_planner import AgentPlanner
from src.state_manager import StateManager

# --- Global flag to signal the assistant thread to stop ---
stop_assistant = threading.Event()

def assistant_thread_logic(gui):
    """
    This function contains the entire logic of the assistant.
    It will run in a separate, non-GUI thread.
    """
    # --- Initialization of all non-GUI components ---
    print("Initializing Assistant components in background thread...")
    try:
        wake_word_path = "src\Wakanda_en_windows_v3_0_0.ppn" 
        wake_word_detector = WakeWordDetector(keyword_path=wake_word_path)
        stt = SpeechToText(model_size="base")
        tts = LocalTTS()
        agent_planner = AgentPlanner()
        state_manager = StateManager()
    except Exception as e:
        print(f"FATAL: Could not initialize assistant components. Error: {e}")
        gui.update_status(f"Initialization Failed: {e}", "red")
        return

    # --- This is the main loop, running in the background ---
    while not stop_assistant.is_set():
        try:
            gui.update_status("Idle. Listening for wake word...", "blue")
            wake_word_detector.wait_for_wake_word()

            if stop_assistant.is_set(): break

            gui.update_status("Wake word detected! Listening...", "orange")
            tts.speak_feedback("Yes?")
            
            user_text = stt.listen_and_transcribe()
            if not user_text:
                continue

            # NEW STEP: Correct the transcription with an LLM
            from src.agent.agent_planner import correct_transcription_with_llm # Add this import at the top of main.py
            user_text = correct_transcription_with_llm(user_text)

            state_manager.add_message("user", user_text)
            gui.update_status(f"Thinking about: '{user_text}'", "purple")

            action_result = route_command(user_text)

            if action_result == "AGENT":
                final_response = agent_planner.run_agent(user_text, state_manager.get_history())
            else:
                final_response = action_result

            state_manager.add_message("assistant", final_response)
            gui.update_status(f"Responding...", "green")
            tts.speak_primary(final_response)

        except Exception as e:
            print(f"An error occurred in the assistant loop: {e}")
            gui.update_status(f"Error: {e}", "red")
            if 'tts' in locals():
                tts.speak_feedback("I've run into an unexpected error.")
            time.sleep(2) # Pause after an error

    print("Assistant thread has stopped.")


if __name__ == "__main__":
    print("Initializing TAM-VA...")
    
    # 1. Initialize the GUI first, in the main thread
    gui = StatusGUI()

    # 2. Create and start the assistant logic in a background thread
    assistant_thread = threading.Thread(target=assistant_thread_logic, args=(gui,))
    assistant_thread.start()

    # 3. Run the GUI's mainloop in the main thread. This is a blocking call.
    # The application will stay open here until the GUI window is closed.
    gui.run()

    # 4. After the GUI window is closed, signal the assistant thread to stop
    print("GUI closed. Signaling assistant thread to stop...")
    stop_assistant.set()

    # 5. Wait for the background thread to finish its current task and exit cleanly
    assistant_thread.join()

    print("Application has been shut down successfully.")