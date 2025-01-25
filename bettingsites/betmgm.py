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

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)


    driver.get("https://sports.co.betmgm.com/en/sports/football-11")

    WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "grid-event-wrapper"))
    )


    games = driver.find_elements(By.CLASS_NAME, "grid-event-wrapper")


    results = []


    for index, game in enumerate(games):
        #print(game.get_attribute("outerHTML"))
        try:
            team_elements = game.find_elements(By.CLASS_NAME, "participant")
            teams = [team.get_attribute('innerHTML')[1:len(team.get_attribute('innerHTML'))-73] for team in team_elements]


            juice_elements = game.find_elements(By.CLASS_NAME, "custom-odds-value-style")
            juice = [juice.text for juice in juice_elements]
            del juice[2]

            spread_and_over_under = game.find_elements(By.CLASS_NAME, "option-attribute")
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



print(get_betmgm_nfl_info())
