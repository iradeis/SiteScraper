import requests
from bs4 import BeautifulSoup
import pandas as pd

import re
import json

'''
from selenium import webdriver
from selenium.webdriver.chrome.service import Service 
# import from webdriver_manager (using underscore)
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome(service = Service(ChromeDriverManager().install()))

options = webdriver.ChromeOptions()
options.add_argument('--headless')# create a driver object using driver_path as a parameter
driver = webdriver.Chrome(options = options, service = Service(ChromeDriverManager().install()))
web = 'https://www.amazon.com'
driver.get(web)

keyword = "running shoes"
search_box = driver.find_element(By.ID, 'twotabsearchtextbox')
search_box.send_keys(keyword)
search_button = driver.find_element(By.ID, 'nav-search-submit-button')
search_button.click()
driver.implicitly_wait(5)

product_link = []
items = wait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "s-result-item s-asin")]')))
for item in items:
    link = item.find_element(By.XPATH, './/a[@class="a-link-normal a-text-normal"]').get_attribute("href")
    product_link.append(link)

driver.quit()

print(product_link)

'''
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