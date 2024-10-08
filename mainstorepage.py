from itertools import product
import requests
from bs4 import BeautifulSoup
import pandas as pd

import re
import json
import time

from PageScrap import PageScrap
import asyncio

from DBAgent import DBAgent


class MainStorePage:
    def __init__(self, base_url):
        self.base_url = base_url
        self.main_content = "div[data-component-type='s-search-result']"
        self.hyperlink = "a.a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal"

    async def product_raws(self, search_terms, max_retries=5):
        url_list = []
        current_page = 1
        # I moved url here for pagination purposes
        # qid value is simply the timestamp (it just uses unix epoch time)
        epoch_time = int(time.time())
        #print(27, epoch_time)
        url = f"https://www.amazon.com/s?k={search_terms}&page={current_page}&qid={epoch_time}&ref=sr_pg_{current_page}"
        
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
                last_page_to_int = 1 # setting a default (there should always be one page of results)

                last_page = soup.find('span', class_='s-pagination-item s-pagination-disabled')
                if last_page != None:
                    last_page_to_int = int(last_page.get_text(strip=True))

                # PAGINATION
                # TODO: edge case scenario is that some search queries don't have "Next" disabled
                else:
                   max_page_without_disabled_next = 5
                   while max_page_without_disabled_next > 0:
                        if soup.find('a', {'aria-label': f'Go to page {max_page_without_disabled_next}'}):
                            last_page = max_page_without_disabled_next
                            last_page_to_int = last_page
                            break
                        else:
                            #print(max_page_without_disabled_next)
                            max_page_without_disabled_next -= 1
                
                while current_page <= last_page_to_int:
                    url = f"https://www.amazon.com/s?k={search_terms}&page={current_page}&qid=1718141001&ref=sr_pg_{current_page}"
                    # scrape from each page via bs4
                    try:
                        soup.select_one("div[data-component-type='s-search-result']")
                    except Exception as e:
                        return f"Content loading error. Please try again in few minutes. Error message: {e}"
                    
                    products = soup.select(self.main_content)
                    # for product in products:
                    #     product_url = f"https://www.amazon.com{product.select_one(self.hyperlink).get('href')}"
                    #     asin = product.get('data-asin')
                    #     url_list.append({"url": product_url, "asin": asin})

                    # USE THIS CODE SNIPPET TO VISUALIZE PAGINATION IN EFFECT
                    for i in range(0, min(3, len(products))):
                        product_url = f"https://www.amazon.com{products[i].select_one(self.hyperlink).get('href')}"
                        asin = products[i].get('data-asin')
                        url_list.append({"url": product_url, "asin": asin})
                        # print(f"the item: {product_url} appears on page: {current_page}")

                    current_page += 1
                        

                if url_list:
                    return url_list
                
            except Exception as e:
                print(f"Retry {retry + 1} || Error: {str(e)}\n URL: {url}")
                if retry < max_retries - 1:
                    await asyncio.sleep(5)
                else:
                    return f"Failed to retrieve valid data after {max_retries} retries. Scraped URLS are saved and ready for crawling process."

        return []

    # async def product_urls(self, url, max_retries=13):
    #     url_lists = []
    #     for retry in range(max_retries):
    #         try:
    #             # Use the 'static_connection' method to download the HTML content of the search results bage
    #             custom_headers = {
    #                 "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
    #                 "accept-language": "en-US,en;q=0.5",
    #             }
    #             # webpage request
    #             response = requests.get(url, headers=custom_headers)
    #             if response.status_code != 200:
    #                 print("Cannot access")
    #                 exit()

    #             soup = BeautifulSoup(response.text, "lxml")

    #             test = soup.find('div', class_="a-section a-spacing-small a-spacing-top-small")
    #             # Check if main content element exists on page:
    #             try:
    #                 soup.select_one(self.main_content)
    #             except Exception as e:
    #                 return f"Content loading error. Please try again in few minutes. Error message: {e}"
    #             # Get product card contents from current page:
    #             card_contents = [
    #                 f"""https://www.amazon.com{product.select_one(self.hyperlink).get('href')}"""
    #                 for product in soup.select(self.main_content)
    #             ]
    #             # url_lists.append(card_contents)
    #             if card_contents:
    #                 return card_contents
    #         except Exception as e:
    #             print(f"Retry {retry + 1} || Error: {str(e)}\n URL: {url}")
    #             if retry < max_retries - 1:
    #                 await asyncio.sleep(5)
    #             else:
    #                 return f"Failed to retrieve valid data after {max_retries} retries. Scraped URLS are saved and ready for crawling process."

    #     return []

    async def search(self, search_terms):
        pairs = await self.product_raws(search_terms)
        search_terms = search_terms.split()
        if not pairs:  # Check if error occurred in product_urls
            print("no links found")  # Print the error message
            return
        
        pairs = pairs[:15]
        sc = PageScrap()

        agent = DBAgent("mongodb://59.120.52.19:27017", username='richard', password='nuclear97')
        for pair in pairs:
            data = {
                'search term': search_terms,
                'url': pair['url'],
                'html': sc.get_html(pair['url']),
                'asin': pair['asin']
            }
            if not agent.IsASINExistRaw(pair['asin']):
                agent.WriteRaw(data)
                
    # parse all current html raws that aren't parsed yet
    async def parse_raw(self):
        agent = DBAgent("mongodb://59.120.52.19:27017", username='richard', password='nuclear97')
        raw_list = agent.getRawList()
        parsed_list = agent.getParsedList()
        
        raw_set = set(raw_list)
        parsed_set = set(parsed_list)
        unparsed_set = raw_set - parsed_set
        
        sc = PageScrap()
        
        for item in unparsed_set:
            sc.parse_html(item)



terms = "running shoes"
store_page = MainStorePage("www.amazon.com/")


async def main():
    await store_page.search(terms)


asyncio.run(main())
