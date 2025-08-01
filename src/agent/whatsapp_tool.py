from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from thefuzz import fuzz

last_seen_message = ""

def start_whatsapp_session(contact_name: str):
    """
    Opens WhatsApp Web with robust options to prevent crashes and finds the best contact match.
    """
    # --- FIX 1: Clean the contact name from stray characters like quotes ---
    cleaned_contact_name = contact_name.strip().strip('"\'')
    
    print(f"Starting WhatsApp session. Searching for a contact similar to: '{cleaned_contact_name}'")
    
    options = webdriver.ChromeOptions()
    
    # --- FIX 2: Add robust startup options to prevent crashes ---
    # This helps Selenium run in a more isolated and stable way.
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--remote-debugging-port=9222") # Use a specific debugging port

    # This saves your session so you don't have to scan the QR code every time
    options.add_argument("user-data-dir=./whatsapp_user_data")
    
    # Manual Chrome Path (remains the same)
    try:
        chrome_executable_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        options.binary_location = chrome_executable_path
    except Exception:
        print("Manual Chrome path not found. Relying on automatic detection.")
    
    try:
        # We now use this `driver` variable throughout the function
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    except WebDriverException as e:
        print(f"CRITICAL ERROR: WebDriver failed to initialize. Error: {e}")
        print("This might be due to a version mismatch between Chrome and ChromeDriver.")
        print("Try deleting the 'webdriver_manager' cache at C:/Users/YourUser/.wdm")
        return None

    driver.get("https://web.whatsapp.com/")
    
    print("Please scan the QR code if needed. Waiting for login...")
    
    try:
        # Search for the contact using the CLEANED name
        search_box_xpath = '//div[@contenteditable="true"][@data-tab="3"]'
        chat_search_box = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, search_box_xpath)))
        chat_search_box.click()
        chat_search_box.send_keys(cleaned_contact_name)
        time.sleep(3)

        # Fuzzy Matching Logic (remains the same)
        best_match_element = None
        highest_score = 0
        contacts_pane_xpath = "//div[@id='pane-side']//div[@role='listitem']"
        search_results = driver.find_elements(By.XPATH, contacts_pane_xpath)

        if not search_results:
            raise TimeoutException("No search results found.")

        for result in search_results:
            try:
                title_element = result.find_element(By.XPATH, ".//span[@title]")
                full_contact_name = title_element.get_attribute("title")
                score = fuzz.ratio(cleaned_contact_name.lower(), full_contact_name.lower())
                if score > highest_score:
                    highest_score = score
                    best_match_element = title_element
            except NoSuchElementException: continue
        
        MINIMUM_CONFIDENCE_SCORE = 70
        if highest_score > MINIMUM_CONFIDENCE_SCORE:
            best_match_name = best_match_element.get_attribute("title")
            print(f"Best match found: '{best_match_name}' with a score of {highest_score}. Clicking it.")
            best_match_element.click()
            return driver
        else:
            print(f"Could not find a confident match. Highest score was {highest_score}.")
            driver.quit()
            return None

    except Exception as e:
        print(f"An unexpected error occurred during session start: {e}")
        driver.quit()
        return None

# The send and read functions remain unchanged
def send_whatsapp_message(driver: webdriver.Chrome, message: str):
    # ... (function content is the same as before) ...
    try:
        message_box_xpath = '//div[@contenteditable="true"][@data-tab="10"]'
        message_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, message_box_xpath)))
        message_box.click(); message_box.clear(); message_box.send_keys(message)
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