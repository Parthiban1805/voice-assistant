# src/agent/whatsapp_tool.py
# This file contains all functions for controlling WhatsApp Web using Selenium.

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# Import the fuzzy matching library
from thefuzz import fuzz

# Global variable to track the last message seen to avoid re-reading
last_seen_message = ""

def start_whatsapp_session(contact_name: str):
    """
    Opens WhatsApp Web, uses a manual Chrome path, and fuzzy matching to find the best contact match.
    Returns the driver object for the active session.
    """
    print(f"Starting WhatsApp session. Searching for a contact similar to: '{contact_name}'")
    options = webdriver.ChromeOptions()
    options.add_argument("user-data-dir=./whatsapp_user_data")
    
    # --- HARDCODED CHROME PATH (THE FIX) ---
    # This explicitly tells Selenium where your Chrome browser is installed.
    try:
        chrome_executable_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        options.binary_location = chrome_executable_path
        print(f"Using manually specified Chrome path: {chrome_executable_path}")
    except Exception as e:
        print(f"Could not use manual Chrome path. Error: {e}. Relying on automatic detection.")
    # ----------------------------------------
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://web.whatsapp.com/")
    
    print("Please scan the QR code if needed. Waiting for login...")
    
    try:
        # --- Search for the contact ---
        search_box_xpath = '//div[@contenteditable="true"][@data-tab="3"]'
        chat_search_box = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, search_box_xpath)))
        chat_search_box.click()
        chat_search_box.send_keys(contact_name)
        time.sleep(3) # Wait for search results to appear

        # --- FUZZY MATCHING LOGIC ---
        best_match_element = None
        highest_score = 0
        
        contacts_pane_xpath = "//div[@id='pane-side']//div[@role='listitem']"
        search_results = driver.find_elements(By.XPATH, contacts_pane_xpath)

        if not search_results:
            raise TimeoutException("No search results found for the contact name.")

        print(f"Found {len(search_results)} potential matches. Analyzing for the best fit...")
        
        for result in search_results:
            try:
                title_element = result.find_element(By.XPATH, ".//span[@title]")
                full_contact_name = title_element.get_attribute("title")
                score = fuzz.ratio(contact_name.lower(), full_contact_name.lower())
                print(f"  - Comparing '{contact_name}' with '{full_contact_name}' -> Score: {score}")

                if score > highest_score:
                    highest_score = score
                    best_match_element = title_element
            except NoSuchElementException:
                continue
        
        MINIMUM_CONFIDENCE_SCORE = 70 

        if highest_score > MINIMUM_CONFIDENCE_SCORE:
            best_match_name = best_match_element.get_attribute("title")
            print(f"Best match found: '{best_match_name}' with a score of {highest_score}. Clicking it.")
            best_match_element.click()
            return driver
        else:
            print(f"Could not find a confident match. Highest score was {highest_score}, which is below the threshold of {MINIMUM_CONFIDENCE_SCORE}.")
            driver.quit()
            return None

    except TimeoutException as e:
        print(f"Failed to find contact: {e}")
        driver.quit()
        return None
    except Exception as e:
        print(f"An unexpected error occurred during session start: {e}")
        driver.quit()
        return None


def send_whatsapp_message(driver: webdriver.Chrome, message: str):
    """Sends a message to the currently active chat."""
    try:
        message_box_xpath = '//div[@contenteditable="true"][@data-tab="10"]'
        message_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, message_box_xpath)))
        message_box.click()
        # Clear the box before sending to avoid appending to old text
        message_box.clear()
        message_box.send_keys(message)
        
        send_button_xpath = '//span[@data-icon="send"]'
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, send_button_xpath)))
        driver.find_element(By.XPATH, send_button_xpath).click()
        print(f"Sent message: '{message}'")
        return True
    except Exception as e:
        print(f"Error sending message: {e}")
        return False


def read_latest_reply(driver: webdriver.Chrome) -> str | None:
    """Reads the latest message from the other person in the chat."""
    global last_seen_message
    try:
        # Finds all message bubbles that are NOT your own.
        all_messages = driver.find_elements(By.CSS_SELECTOR, ".message-in .copyable-text")
        
        if not all_messages:
            return None 
            
        latest_message_element = all_messages[-1]
        latest_message_text = latest_message_element.text
        
        if latest_message_text != last_seen_message:
            last_seen_message = latest_message_text
            print(f"Read new reply: '{latest_message_text}'")
            return latest_message_text
        else:
            return None # No new messages
            
    except NoSuchElementException:
        return None # No messages found
    except Exception as e:
        print(f"Error reading message: {e}")
        return None