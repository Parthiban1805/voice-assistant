# main.py
import threading
import time
from src.gui import StatusGUI
from src.wake_word import WakeWordDetector
from src.speech_to_text import SpeechToText
from src.local_tts import LocalTTS
from src.command_router import route_command
from src.agent.agent_planner import AgentPlanner, correct_transcription_with_llm
from src.state_manager import StateManager

# --- Import the new WhatsApp and Flirting functions ---
from src.agent.whatsapp_tool import start_whatsapp_session, send_whatsapp_message, read_latest_reply
from src.agent.agent_planner import generate_flirty_reply


# --- Global flag to signal all background threads to stop ---
stop_assistant = threading.Event()


def run_flirting_session(contact_name: str, gui):
    """
    The main loop for the autonomous WhatsApp flirting agent.
    This function takes over the assistant's logic until the app is closed.
    """
    gui.update_status(f"Entering Flirt Mode with {contact_name}...", "magenta")
    
    driver = start_whatsapp_session(contact_name)
    if not driver:
        gui.update_status(f"Failed to start WhatsApp session with {contact_name}.", "red")
        return

    # The history for this specific conversation, separate from the main state
    flirt_history = []

    # Generate and send the first message
    gui.update_status(f"Thinking of an opening line for {contact_name}...", "cyan")
    first_message = generate_flirty_reply([]) # Start with an empty history for an opener
    
    if send_whatsapp_message(driver, first_message):
        flirt_history.append({"role": "agent", "text": first_message})
    else:
        gui.update_status(f"Failed to send initial message to {contact_name}.", "red")
        driver.quit()
        return
    
    gui.update_status(f"Message sent. Now waiting for a reply from {contact_name}...", "cyan")

    # The main listening loop for replies
    while not stop_assistant.is_set():
        reply = read_latest_reply(driver)
        
        if reply:
            gui.update_status(f"New reply from {contact_name}: '{reply}'", "green")
            flirt_history.append({"role": "girlfriend", "text": reply})
            
            # Think of a new flirty response
            gui.update_status("Thinking of a clever reply...", "cyan")
            new_message = generate_flirty_reply(flirt_history)
            
            # Send the new message
            if send_whatsapp_message(driver, new_message):
                flirt_history.append({"role": "agent", "text": new_message})
                gui.update_status(f"Reply sent. Waiting for the next response...", "cyan")
            else:
                gui.update_status(f"Failed to send reply to {contact_name}.", "red")

        # Wait for a bit before checking again to avoid spamming WhatsApp's servers
        # and to give the user time to reply.
        time.sleep(15) # Check for new messages every 15 seconds

    print("Exiting Flirt Mode.")
    driver.quit()


def assistant_thread_logic(gui):
    """
    This function contains the main logic of the assistant.
    It listens for commands and decides which action to take.
    """
    print("Initializing Assistant components in background thread...")
    try:
        wake_word_path = "src\Wakanda_en_windows_v3_0_0.ppn" # <-- CHANGE THIS IF YOURS IS DIFFERENT
        wake_word_detector = WakeWordDetector(keyword_path=wake_word_path)
        stt = SpeechToText(model_size="small")
        tts = LocalTTS()
        agent_planner = AgentPlanner()
        state_manager = StateManager()
    except Exception as e:
        print(f"FATAL: Could not initialize assistant components. Error: {e}")
        gui.update_status(f"Initialization Failed: {e}", "red")
        return

    # --- This is the main command loop, running in the background ---
    while not stop_assistant.is_set():
        try:
            gui.update_status("Idle. Listening for wake word...", "blue")
            wake_word_detector.wait_for_wake_word()

            if stop_assistant.is_set(): break

            gui.update_status("Wake word detected! Listening...", "orange")
            tts.speak_feedback("Yes?")
            
            raw_user_text = stt.listen_and_transcribe()
            user_text = correct_transcription_with_llm(raw_user_text)

            if not user_text:
                continue

            # Route the command to the appropriate handler
            action_result = route_command(user_text)

            # --- DECISION LOGIC ---
            # 1. Check if we need to enter the special "Flirt Mode"
            if isinstance(action_result, tuple) and action_result[0] == "FLIRT_MODE":
                contact_name = action_result[1]
                # This call will block until the session is ended by the user closing the GUI
                run_flirting_session(contact_name, gui)
                # After the session ends, we go back to the top of the loop
                continue

            # 2. Check if we need to call the general-purpose AI agent
            elif action_result == "AGENT":
                state_manager.add_message("user", user_text)
                gui.update_status(f"Thinking about: '{user_text}'", "purple")
                final_response = agent_planner.run_agent(user_text, state_manager.get_history())
                state_manager.add_message("assistant", final_response)
                gui.update_status(f"Responding...", "green")
                tts.speak_primary(final_response)

            # 3. Handle simple, fast-path commands
            else:
                gui.update_status(f"Executing: '{user_text}'", "green")
                final_response = action_result
                tts.speak_primary(final_response)

        except Exception as e:
            print(f"An error occurred in the assistant loop: {e}")
            gui.update_status(f"Error: {e}", "red")
            if 'tts' in locals():
                tts.speak_feedback("I have run into an unexpected error.")
            time.sleep(2)

    print("Assistant thread has stopped.")


if __name__ == "__main__":
    print("Initializing TAM-VA...")
    
    # Initialize the GUI in the main thread
    gui = StatusGUI()

    # Create and start the assistant logic in a background thread
    assistant_thread = threading.Thread(target=assistant_thread_logic, args=(gui,))
    assistant_thread.start()

    # Run the GUI's mainloop in the main thread.
    gui.run()

    # After the GUI window is closed, signal the assistant thread to stop
    print("GUI closed. Signaling assistant thread to stop...")
    stop_assistant.set()

    # Wait for the background thread to finish its current task and exit cleanly
    assistant_thread.join()

    print("Application has been shut down successfully.")