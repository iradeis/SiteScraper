import requests
from bs4 import BeautifulSoup
import pandas as pd

import re
import json

from PageScrap import PageScrap
import asyncio

"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service 
# import from webdriver_manager (using underscore)
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome(service = Service(ChromeDriverManager().install()))

options = webdriver.ChromeOptions()
# create a driver object using driver_path as a parameter
driver = webdriver.Chrome(options = options, service = Service(ChromeDriverManager().install()))
web = 'https://www.amazon.com'
driver.get(web)

keyword = "running shoes"
search_box = driver.find_element(By.ID, 'twotabsearchtextbox')
search_box.send_keys(keyword)
search_button = driver.find_element(By.ID, 'nav-search-submit-button')
search_button.click()
driver.implicitly_wait(5)

category_url = driver.current_url
driver.quit()

custom_headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0',
    'accept-language': 'en-US,en;q=0.5',
}

# webpage request
response = requests.get(category_url, headers= custom_headers)
if(response.status_code != 200):
    print("Cannot access")
    exit()

soup = BeautifulSoup(response.text, 'lxml')

links = []
all_products = soup.find('div', class_="s-main-slot s-result-list s-search-results sg-row")
for tag in soup.find_all('data-component-type="s-search-result"'):
    link_component = tag.find('a', class_="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal")
    link = link_component['href']
    links.append(link)

print(links)
"""

"""
url = 'https://www.amazon.com/s?k=running+shoes&crid=3QCBTHLTF3B6X&sprefix=running+shoe%2Caps%2C213&ref=nb_sb_noss_1'

custom_headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0',
    'accept-language': 'en-US,en;q=0.5',
}
# webpage request
response = requests.get(url, headers= custom_headers)
if(response.status_code != 200):
    print("Cannot access")
    exit()

soup = BeautifulSoup(response.text, 'lxml')

parent_element = soup.find('div', class_='s-main-slot s-result-list s-search-results sg-row')
all_product_elements = parent_element.find_all('div', {'data-component-type': 's-search-result'})
"""

"""
product_one = all_product_elements[0]
link_element = product_one.find('a', class_="a-link-normal s-no-outline")
if link_element:
    href = link_element.get('href')
    if href.startswith('/'):
        direct_link = "https://www.amazon.com" + href
        print(direct_link)
"""


class MainStorePage:
    def __init__(self, base_url):
        self.base_url = base_url
        self.main_content = "div[data-component-type='s-search-result']"
        self.hyperlink = "a.a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal"

    async def product_urls(self, url, max_retries=13):
        url_lists = []
        for retry in range(max_retries):
            try:
                # Use the 'static_connection' method to download the HTML content of the search results bage
                custom_headers = {
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
                    "accept-language": "en-US,en;q=0.5",
                }
                # webpage request
                response = requests.get(url, headers=custom_headers)
                if response.status_code != 200:
                    print("Cannot access")
                    exit()

                soup = BeautifulSoup(response.text, "lxml")

                test = soup.find('div', class_="a-section a-spacing-small a-spacing-top-small")
                # Check if main content element exists on page:
                try:
                    soup.select_one(self.main_content)
                except Exception as e:
                    return f"Content loading error. Please try again in few minutes. Error message: {e}"
                # Get product card contents from current page:
                card_contents = [
                    f"""https://www.amazon.com{product.select_one(self.hyperlink).get('href')}"""
                    for product in soup.select(self.main_content)
                ]
                # url_lists.append(card_contents)
                if card_contents:
                    return card_contents
            except Exception as e:
                print(f"Retry {retry + 1} || Error: {str(e)}\n URL: {url}")
                if retry < max_retries - 1:
                    await asyncio.sleep(5)
                else:
                    return f"Failed to retrieve valid data after {max_retries} retries. Scraped URLS are saved and ready for crawling process."

        return []

    async def search(self, search_terms):
        url = "https://www.amazon.com/s?k=" + search_terms
        urls = await self.product_urls(url)
        if not urls:  # Check if error occurred in product_urls
            print("no links found")  # Print the error message
            return
        sc = PageScrap()
        for link in urls:
            print(link)
            jsonstr = sc.scrape_site(link)
            #j = json.loads(jsonstr)
            #print(j['url'])


terms = "running shoes"
store_page = MainStorePage("www.amazon.com/")


async def main():
    await store_page.search(terms)


asyncio.run(main())
