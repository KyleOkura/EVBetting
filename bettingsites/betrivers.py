from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



def get_betrivers_nfl_info():
    chrome_options = Options()
    chrome_options.add_argument("--headless")


    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)


    driver.get("https://co.betrivers.com/?page=sportsbook&group=1000093656&type=matches#home")

    print(driver.page_source)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "sc-dluQYU"))
    )


    games = driver.find_elements(By.CLASS_NAME, "sc-dluQYU")

    results = []


    for index, game in enumerate(games):
        try:
            team_elements = game.find_elements(By.CLASS_NAME, "KambiBC-event-participants__name-participant-name")
            teams = [team.text for team in team_elements]


            juice_elements = game.find_elements(By.CLASS_NAME, "sc-kAyceB")
            juice = [juice.text for juice in juice_elements]

            spread_and_over_under = game.find_elements(By.CLASS_NAME, "sc-dcJsrY")
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


print(get_betrivers_nfl_info())