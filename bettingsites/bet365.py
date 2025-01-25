







'''
url = 'https://play.ballybet.com/sports#sports-hub/american_football/nfl'
page = requests.get(url)

soup = BeautifulSoup(page.content, "html.parser")
results = soup.find('ul', class_='KambiBC-sandwich-filter__list')

print(soup)






from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

# Set up Selenium options
options = Options()
options.add_argument('--headless')  # Run in headless mode (no browser UI)
options.add_argument('--disable-gpu')  # Disable GPU (for headless mode on Windows)
options.add_argument('--no-sandbox')  # Bypass OS security model (Linux)

# Specify the path to your WebDriver
service = Service("C:\Users\Kyle\Downloads\chrome-win64\chrome-win64\chrome")  # Replace with the path to your ChromeDriver

# Start WebDriver
driver = webdriver.Chrome(service=service, options=options)

try:
    # Navigate to the website
    url = 'https://play.ballybet.com/sports#sports-hub/american_football/nfl'
    driver.get(url)

    # Allow time for the page to load fully
    time.sleep(5)

    # Locate the desired elements
    odds_elements = driver.find_elements(By.CLASS_NAME, 'KambiBC-sandwich-filter__list')

    # Extract and print the content
    for element in odds_elements:
        print(element.text)

finally:
    # Close the WebDriver
    driver.quit()

'''