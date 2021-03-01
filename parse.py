from bs4 import BeautifulSoup
from pprint import pprint
from random import randint
import re
import requests
from time import sleep


page_number = 1
max_articles = 100
links = []
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36'}


def open_page(page_number):
    url = f'https://www.zvezdaaltaya.ru/category/novosti/page/{page_number}/'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print('success')
        page = response.text
    else:
        raise AttributeError('bad status code')
    sleep(randint(3, 10))
    return page

# with open('links.html', 'w') as f:
#    f.write(response.text)
page = open('links.html').read()

def get_links(page):
    new_links = []
    soup = BeautifulSoup(page, 'html.parser')
    for link in soup.find_all('a'):
        # if res := re.findall(r'https://www.zvezdaaltaya.ru/\d{4}/\d{2}/.+', link.get('href')):
        #     if not re.findall(r'https://www.zvezdaaltaya.ru/\d{4}/\d{2}/\d{2}/', res[0]):
        #         if res[0] not in links:
        #             new_links.append(res[0])
        if res := re.findall(r'https://www.zvezdaaltaya.ru/.+', link.get('href')):
           new_links.append(res[0])
    # with open('links.txt', 'a') as f:
    #   f.write('\n'.join(new_links) + '\n')
    return new_links

# while len(links) < max_articles:
#     try:
#         page = open_page(page_number)
#     except AttributeError:
#         page_number += 1
#         continue
#     else:
#         links = get_links(page)
#         page_number += 1
# else:
#     if len(links) > max_articles:
#         with open('links.txt', 'w') as f:
#             f.write('\n'.join(links[:max_articles]))


pprint(get_links(page))