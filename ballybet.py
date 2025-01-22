from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

chrome_options = Options()
chrome_options.add_argument("--headless")

# Automatically download and use the correct version of ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Navigate to the page
driver.get("https://play.ballybet.com/sports#sports-hub/american_football/nfl")

# Wait for a specific element to load (adjust the selector based on the page structure)

    # Example: Wait until the odds section is visible (modify the selector to fit your case)
element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "KambiBC-sandwich-filter__list"))
)

    # You can interact with elements here, e.g., click on an element or extract text
    # For example, extract the text from the found element:
print(element.text)

exit()

driver.quit()

