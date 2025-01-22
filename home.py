from bs4 import BeautifulSoup
import requests

url = 'https://api.the-odds-api.com/v4/sports/upcoming/odds/?regions=us&markets=h2h&oddsFormat=american&apiKey=cb81bec595198c37776a7c7216aa95a5'
page = requests.get(url)

soup = BeautifulSoup(page.content, "html.parser")
results = soup.find_all("id")

print(soup)