from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


def get_fanduel_nfl_info():
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get("https://sportsbook.fanduel.com/navigation/nfl")

    #elements = driver.find_elements(By.CLASS_NAME, "af")
    elements = driver.find_elements((By.XPATH, "//div[contains(text(), 'Spread')]"))

    '''
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'NFL')]"))
        #EC.presence_of_element_located((By.CLASS_NAME, "am aq ao ap af ka s gq kb gm h i j ah ai m aj o ak q al"))
    )
    '''

    print(elements)

    html_page = driver.page_source

    print(html_page)

    soup = BeautifulSoup(html_page, 'html.parser')


    info = soup.find_all("div", class_="kl af s h i j ah ai m aj o ak q al")


    print(info)


    driver.quit()


get_fanduel_nfl_info()