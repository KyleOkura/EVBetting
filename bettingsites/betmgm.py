from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



def get_betmgm_nfl_info():
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    # Automatically download and use the correct version of ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Navigate to the page
    driver.get("https://sports.co.betmgm.com/en/sports/football-11")

    #print(driver.page_source)

    # Wait for a specific element to load (adjust the selector based on the page structure)

        # Example: Wait until the odds section is visible (modify the selector to fit your case)
    '''
    element = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, "grid-event-wrapper"))
    )
    '''
    WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "grid-event-wrapper"))
    )

        # You can interact with elements here, e.g., click on an element or extract text
        # For example, extract the text from the found element:

    games = driver.find_elements(By.CLASS_NAME, "grid-event-wrapper")







    results = []


    for index, game in enumerate(games):
            try:
                # Extract team names
                team_elements = game.find_elements(By.CLASS_NAME, "participant")
                teams = [team.text for team in team_elements]

                # Extract odds
                odds_elements = game.find_elements(By.CLASS_NAME, "custom-odds-value-style")
                odds = [odds.text for odds in odds_elements]

                # Extract over/under
                over_under_elements = game.find_elements(By.CLASS_NAME, "option-group-attribute")
                over_under = [ou.text for ou in over_under_elements]

                # Append to results
                results.append({
                    "game_index": index,
                    "teams": teams,
                    "odds": odds,
                    "over_under": over_under,
                })

            except Exception as game_error:
                print(f"Error processing game {index}: {game_error}")
                continue













    driver.quit()

    return results

    '''
    text = element.text

    driver.quit()   

    return text
    '''




print(get_betmgm_nfl_info())




'''
session = HTMLSession()
response = session.get('https://play.ballybet.com/sports#sports-hub/american_football/nfl')

response.html.render()

print(response.html.html)



from bs4 import BeautifulSoup
import requests
#from requests_html import HTMLSession
from playwright.sync_api import sync_playwright


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://play.ballybet.com/sports#sports-hub/american_football/nfl')
    print(page.content())
    browser.close()
'''