import requests
from bs4 import BeautifulSoup
import pandas as pd

import re
import json

from PageScrap import PageScrap
import asyncio

from DBAgent import DBAgent


class MainStorePage:
    def __init__(self, base_url):
        self.base_url = base_url
        self.main_content = "div[data-component-type='s-search-result']"
        self.hyperlink = "a.a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal"

    async def product_raws(self, url, max_retries=5):
        url_list = []
        for retry in range(max_retries):
            try:
                # Use the 'static_connection' method to download the HTML content of the search results page
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

                try:
                    soup.select_one("div[data-component-type='s-search-result']")
                except Exception as e:
                    return f"Content loading error. Please try again in few minutes. Error message: {e}"
                
                products = soup.select(self.main_content)
                for product in products:
                    product_url = f"https://www.amazon.com{product.select_one(self.hyperlink).get('href')}"
                    asin = product.get('data-asin')
                    url_list.append({"url": product_url, "asin": asin})

                if url_list:
                    return url_list
                
            except Exception as e:
                print(f"Retry {retry + 1} || Error: {str(e)}\n URL: {url}")
                if retry < max_retries - 1:
                    await asyncio.sleep(5)
                else:
                    return f"Failed to retrieve valid data after {max_retries} retries. Scraped URLS are saved and ready for crawling process."

        return []

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
        pairs = await self.product_raws(url)
        if not pairs:  # Check if error occurred in product_urls
            print("no links found")  # Print the error message
            return
        pairs = pairs[:5]
        sc = PageScrap()
        agent = DBAgent("mongodb://localhost:27017")
        for pair in pairs:
            data = {
                'search terms': search_terms,
                'html': sc.get_html(pair['url']),
                'asin': pair['asin']
            }
            agent.WriteRaw(data)



terms = "running shoes"
store_page = MainStorePage("www.amazon.com/")


async def main():
    await store_page.search(terms)


asyncio.run(main())
