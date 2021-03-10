link = 'http://kamtime.ru/'
from bs4 import BeautifulSoup
import requests
import re

response = requests.get(link)

soup = BeautifulSoup(response.content)
pure = []

links = soup.findAll('a', attrs={'href': re.compile("/node/\d{4}")})


for link in links:
    link2 = re.findall(r'/node/\d{4}',str(links))

clear_links = []

for link_url in link2:
    code = 'http://kamtime.ru' + link_url
    if code not in clear_links:
        clear_links.append(code)

print(clear_links)




