from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import requests
from bs4 import BeautifulSoup


def get_bet365_nfl_info():
    driver = uc.Chrome(headless=False)
    driver.get("https://www.co.bet365.com/")
    
    try:
        WebDriverWait(driver, 30).until(
            lambda d: len(d.find_elements(By.CLASS_NAME, "wc-WebConsoleModule_SiteContainer")) > 0
        )

    except Exception as e:
        print("Timeout waiting for games to load:", e)
        driver.quit()
        return []

    games = driver.find_elements(By.CLASS_NAME, "wc-WebConsoleModule_SiteContainer")
    results = []

    for index, game in enumerate(games):
        try:
            team_elements = game.find_elements(By.CLASS_NAME, "sac-ParticipantFixtureDetailsHigherAmericanFootball_Team")
            teams = [team.text for team in team_elements]

            juice_elements = game.find_elements(By.CLASS_NAME, "sac-ParticipantCenteredStacked50OTBNew_Odds")
            juice = [juice.text for juice in juice_elements]

            spread_and_over_under = game.find_elements(By.CLASS_NAME, "sac-ParticipantCenteredStacked50OTBNew_Handicap")
            odds = [odds.text for odds in spread_and_over_under]

            results.append({
                "game_index": index,
                "teams": teams,
                "odds": odds,
                "juice": juice,
            })

        except Exception as game_error:
            print(f"Error processing game {index}: {game_error}")
            continue

    driver.quit()
    return results

print(get_bet365_nfl_info())





'''
def get_bet365_nfl_info():
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")


    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)


    driver.get("https://www.co.bet365.com/?_h=J9JMb5z5AhHU92IcWFQLpA%3D%3D&btsffd=1#/AC/B12/C20426855/D48/E1441/F36/")
    #driver.get("https://www.co.bet365.com/")


    WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "wc-WebConsoleModule_SiteContainer"))
    )

    WebDriverWait(driver, 20).until(
        lambda d: len(d.find_elements(By.CLASS_NAME, "wc-WebConsoleModule_SiteContainer")) > 0
    )

    
    #print(driver.page_source)

    games = driver.find_elements(By.CLASS_NAME, "wc-WebConsoleModule_SiteContainer")

    print(games)

    results = []


    for index, game in enumerate(games):
        #print(game.get_attribute("outerHTML"))
        try:
            team_elements = game.find_elements(By.CLASS_NAME, "sac-ParticipantFixtureDetailsHigherAmericanFootball_Team ")
            teams = [team.text for team in team_elements]


            juice_elements = game.find_elements(By.CLASS_NAME, "sac-ParticipantCenteredStacked50OTBNew_Odds")
            juice = [juice.text for juice in juice_elements]

            spread_and_over_under = game.find_elements(By.CLASS_NAME, "sac-ParticipantCenteredStacked50OTBNew_Handicap")
            odds = [odds.text for odds in spread_and_over_under]


            results.append({
                "game_index": index,
                "teams": teams,
                "odds": odds,
                "juice": juice,
            })

        except Exception as game_error:
            print(f"Error processing game {index}: {game_error}")
            continue


    driver.quit()

    return results

'''

print(get_bet365_nfl_info())
