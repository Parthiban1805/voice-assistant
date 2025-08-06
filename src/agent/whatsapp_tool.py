# src/agent/whatsapp_tool.py (Revised for Stability and Permissions)
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

CHROME_PROFILES = {
    "parthiban s": "Default",
    "parthiban gaming": "Profile 1",
}
DEFAULT_WHATSAPP_PROFILE = "parthiban s"

def start_whatsapp_session(contact_name: str):
    """
    Opens WhatsApp Web in a specific Chrome Profile sandbox to avoid permission errors.
    """
    cleaned_contact_name = contact_name.strip().strip('"\'')
    print(f"Starting WhatsApp session. Searching for a contact similar to: '{cleaned_contact_name}'")
    
    options = webdriver.ChromeOptions()
    
    internal_profile_dir = CHROME_PROFILES.get(DEFAULT_WHATSAPP_PROFILE)
    if not internal_profile_dir:
        print(f"ERROR: Default WhatsApp profile '{DEFAULT_WHATSAPP_PROFILE}' not found in CHROME_PROFILES dictionary.")
        return None
        
    print(f"Using Chrome profile '{DEFAULT_WHATSAPP_PROFILE}' (Directory: {internal_profile_dir}) for this session.")
    
    # ========================== THIS IS THE FIX ==========================
    # We revert to using a local directory for the session data.
    # This creates a "sandbox" inside your project folder, avoiding all permission issues.
    # The profile directory will be created INSIDE this sandbox.
    options.add_argument("user-data-dir=./chrome_sessions") 
    options.add_argument(f"--profile-directory={internal_profile_dir}")
    # =====================================================================
    
    # Robust startup options
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")
    options.add_argument("--remote-debugging-port=9222")

    # Manual Chrome Path
    try:
        chrome_executable_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        options.binary_location = chrome_executable_path
    except Exception:
        print("Manual Chrome path not found.")
    
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    except WebDriverException as e:
        print(f"CRITICAL ERROR: WebDriver failed to initialize. Error: {e}")
        return None

    driver.get("https://web.whatsapp.com/")
    print("Waiting for WhatsApp Web to load...")
    
    try:
        # Fuzzy Matching Logic (no changes needed here)
        search_box_xpath = '//div[@contenteditable="true"][@data-tab="3"]'
        chat_search_box = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, search_box_xpath)))
        chat_search_box.click()
        chat_search_box.send_keys(cleaned_contact_name)
        time.sleep(3)
        
        # ... (The rest of the fuzzy matching logic is correct and remains unchanged) ...
        best_match_element = None; highest_score = 0
        contacts_pane_xpath = "//div[@id='pane-side']//div[@role='listitem']"
        search_results = driver.find_elements(By.XPATH, contacts_pane_xpath)
        if not search_results: raise TimeoutException("No search results found.")
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
            print(f"Best match found: '{best_match_name}'... Clicking it.")
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

# The send_whatsapp_message and read_latest_reply functions remain exactly the same.
def send_whatsapp_message(driver: webdriver.Chrome, message: str):
    # ... code is unchanged ...
    try:
        message_box_xpath = '//div[@contenteditable="true"][@data-tab="10"]'
        message_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, message_box_xpath)))
        message_box.click(); message_box.clear(); message_box.send_keys(message)
        send_button_xpath = '//span[@data-icon="send"]'
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, send_button_xpath)))
        driver.find_element(By.XPATH, send_button_xpath).click()
        return True
    except Exception as e:
        return False
        
def read_latest_reply(driver: webdriver.Chrome) -> str | None:
    # ... code is unchanged ...
    global last_seen_message
    try:
        all_messages = driver.find_elements(By.CSS_SELECTOR, ".message-in .copyable-text")
        if not all_messages: return None
        latest_message_element = all_messages[-1]
        latest_message_text = latest_message_element.text
        if latest_message_text != last_seen_message:
            last_seen_message = latest_message_text
            return latest_message_text
        return None
    except Exception:
        return None