import requests
import re
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

headers = {
            'authority': 'www.amazon.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
            "accept-language": "en-US,en;q=0.5",
        }

# reviews_url = 'https://www.amazon.com/product-reviews/B098P4P8QM/'
# reviews_url = 'https://www.amazon.com/Treehobby-Aluminium-Anti-Collision-Protective-AX103007/product-reviews/B098P4P8QM/ref=cm_cr_dp_d_show_all_btm?reviewerType=all_reviews'


# USE THE BOTTOM URL TO TEST OUT 100+/1000+ OF REVIEWS. FOR TESTING PURPOSES
# reviews_url = 'https://www.amazon.com/product-reviews/B013KW38RQ/' #3638 reviews
# reviews_url = 'https://www.amazon.com/product-reviews/B0BTBQX8QS/' #140 reviews
reviews_url = 'https://www.amazon.com/product-reviews/B0018C8LK0/' #775 reviews

# Defined num of pages to scrape dynamically
# note that each page always have 10 reviews whenever it has 10+ reviews.
# may wanna set a cap for max page to paginate because some products have thousands of reviews which took a while to scrape
def findTotalNumberOfPagesToIterate(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')

    filter_info_section = soup.find('div', id='filter-info-section')

    review_rating_count_div = filter_info_section.find('div', {'data-hook': 'cr-filter-info-review-rating-count'})

    text_content = review_rating_count_div.get_text(strip=True)

    # Find number of descriptive reviews so that beautifulsoup doesn't just keep scraping the last page
    match = re.search(r'(\d{1,3}(?:,\d{3})*) with reviews', text_content)
    if match:
        reviews_text = match.group(1)
        reviews_count = int(reviews_text.replace(',', ''))
        # print(int(reviews_count / 10) + 1)

        return int(reviews_count / 10) + 1
    else:
        print("No match found")
        return 1


def retrievePaginationHtml(url, len_page):
    count = 0
    soups = []
    
    for page_no in range(1, len_page + 1):
        pageSpecificURL = url

        pageSpecificURL = pageSpecificURL + f"ref=cm_cr_arp_d_paging_btm_next_2?ie=UTF8&reviewerType=all_reviews&pageNumber={page_no}"
        print(pageSpecificURL)
        
        response = requests.get(pageSpecificURL, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')

        soups.append(pageSpecificURL)
    return soups


def retrieveReviewsOnPage(urls):
    count = 0
    for url in urls:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print("Cannot access")
            exit()

        soup = BeautifulSoup(response.text, "lxml")
        list = soup.find('div', id="cm_cr-review_list")

        listOfReviewerIDs = []

        if list:
            # Find all review elements
            review_list = list.find_all("div", class_="a-section review aok-relative")
            # Access individual reviews
            for review in review_list:
                id = review.get("id")
                print(id)
                
    
 


len_page = findTotalNumberOfPagesToIterate(reviews_url)
html_datas = retrievePaginationHtml(reviews_url, len_page)
retrieveReviewsOnPage(html_datas)



# print(html_datas)

# reviews = []
# for html_data in html_datas:
#     review = getReviews(html_data)
#     reviews += review

# df_reviews = pd.DataFrame(reviews)
# print(df_reviews)

# df_reviews.to_csv('reviews.csv', index=False)



# def getReviews(html_data):

#     data_dicts = []
    
#     boxes = html_data.select('div[data-hook="review"]')
    
#     for box in boxes:
        
#         # Select Name using css selector and cleaning text using strip()
#         # If Value is empty define value with 'N/A' for all.
#         try:
#             name = box.select_one('[class="a-profile-name"]').text.strip()
#         except Exception as e:
#             name = 'N/A'

#         try:
#             stars = box.select_one('[data-hook="review-star-rating"]').text.strip().split(' out')[0]
#         except Exception as e:
#             stars = 'N/A'   

#         try:
#             title = box.select_one('[data-hook="review-title"]').text.strip().split('\n')[1]
#         except Exception as e:
#             title = 'N/A'

#         try:
#             datetime_str = box.select_one('[data-hook="review-date"]').text.strip().split(' on ')[-1]
#             date = datetime.strptime(datetime_str, '%B %d, %Y').strftime("%m/%d/%Y")
#         except Exception as e:
#             date = 'N/A'

#         try:
#             description = box.select_one('[data-hook="review-body"]').text.strip()
#         except Exception as e:
#             description = 'N/A'

#         # create Dictionary with al review data 
#         data_dict = {
#             'Name' : name,
#             'Stars' : stars,
#             'Title' : title,
#             'Date' : date,
#             'Description' : description
#         }

#         data_dicts.append(data_dict)
    
#     return data_dicts
