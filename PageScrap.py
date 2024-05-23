import requests
from bs4 import BeautifulSoup
import pandas as pd
import base64

import re
import json


class PageScrap:
    def is_printable_ascii(self, char):
        """Checks if a character is a printable ASCII character."""
        return 32 <= ord(char) <= 126

    # takes url, returns json
    def scrape_site(self, url):
        custom_headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
            "accept-language": "en-US,en;q=0.5",
        }

        # webpage request
        response = requests.get(url, headers=custom_headers)
        if response.status_code != 200:
            print("Cannot access")
            exit()

        soup = BeautifulSoup(response.text, "lxml")

        # product name
        title_element = soup.select_one("#productTitle")
        product_name = title_element.text.strip()

        # brand
        brand_element = soup.find("a", id="bylineInfo")
        if brand_element:
            brand_text = brand_element.text.strip()
            brand_name = re.sub(r"Visit|the|Store|Brand:", "", brand_text).strip()
        else:
            brand_name = "None"

        # look at price using span.a-offscreen
        price_element = soup.find(
            "span",
            class_="a-price aok-align-center reinventPricePriceToPayMargin priceToPay",
        )
        price = float(price_element.text.strip()[1:])

        # discount
        discount_element = soup.find(
            "span",
            class_="a-size-large a-color-price savingPriceOverride aok-align-center reinventPriceSavingsPercentageMargin savingsPercentage",
        )
        discount = discount_element.text.strip() if discount_element else ""
        discount = discount[1:-1] if discount else 0
        discount_percent = int(discount)

        # avg rating
        rating_element = soup.select_one("#acrPopover")
        rating_text = rating_element.attrs.get("title")
        rating = rating_text.replace(" out of 5 stars", "")
        rating_avg = float(rating)

        # number of reviews
        total_reviews_element = soup.find("a", id="acrCustomerReviewLink")
        total_reviews = total_reviews_element.text.strip()
        temp = "".join(char for char in total_reviews if char.isdigit())
        total_reviews = int(temp)

        # rating breakdown
        rating_table = soup.find("table", id="histogramTable")
        rating_stars = []
        for row in rating_table.find_all("tr", class_="a-histogram-row a-align-center"):
            percentage_element = row.find(
                "td", class_="a-text-right a-nowrap a-nowrap"
            ).find("a")
            if percentage_element:
                rating_percent = percentage_element.text.strip()
                rating_percent = rating_percent.replace("%", "")
                rating_stars.append(int(rating_percent))
        rating_stars.reverse()

        # free delivery
        free_delivery_element = soup.find(
            "div", id="mir-layout-DELIVERY_BLOCK-slot-PRIMARY_DELIVERY_MESSAGE_LARGE"
        )
        free_delivery = False
        if free_delivery_element:
            free_delivery = free_delivery_element.text.strip().startswith(
                "FREE delivery"
            )

        # free returns
        free_return_element = soup.find("a", id="creturns-policy-anchor-text")
        free_return = False
        if free_return_element:
            free_return = free_return_element.text.strip() == "FREE Returns"

        # amazon choice
        amazon_choice_element = soup.find(
            "span", class_="a-size-small aok-float-left ac-badge-rectangle"
        )
        amazon_choice = False
        if amazon_choice_element:
            amazon_choice = True

        # limited time deal
        deal_element = soup.find("div", id="dealBadge_feature_div")
        deal = False
        if deal_element:
            deal = True

        # asin, data first available
        asin = ""
        date_first_available = ""

        product_details_element = soup.find("div", id="detailBullets_feature_div")
        if product_details_element:
            product_details_element_text = product_details_element.text.strip()
            tokens = []
            current_token = ""
            in_multiple_spaces = False

            for char in product_details_element_text:
                if PageScrap.is_printable_ascii(self, char):
                    if char.isspace():
                        # Handle multiple spaces
                        if in_multiple_spaces:
                            continue
                        else:
                            in_multiple_spaces = True
                            if current_token:
                                tokens.append(current_token)
                                current_token = ""
                    elif char == ":":
                        # Add current token and colon
                        if current_token:
                            tokens.append(current_token)
                        tokens.append(char)
                        current_token = ""
                        in_multiple_spaces = (
                            False  # Reset multiple space flag after colon
                        )
                    else:
                        # Regular character, add to current token
                        current_token += char
                        in_multiple_spaces = (
                            False  # Reset multiple space flag for regular characters
                        )

            # Append the last token if it has content
            if current_token.strip():
                tokens.append(current_token.strip())

            for i in range(1, len(tokens)):  # Iterate using indexes
                token = tokens[i]
                if token == ":":  # Check if token is colon
                    identifier = tokens[
                        i - 1
                    ].strip()  # Extract identifier (remove colon)
                    if i + 1 < len(tokens):
                        if identifier == "Available":
                            date_first_available = (
                                tokens[i + 1]
                                + " "
                                + tokens[i + 2]
                                + " "
                                + tokens[i + 3]
                            )
                        elif identifier == "ASIN":
                            asin = tokens[i + 1]

        # rank in category
        details_list = product_details_element.find_next_sibling(
            "ul",
            class_="a-unordered-list a-nostyle a-vertical a-spacing-none detail-bullet-list",
        )
        seller_rank_text = details_list.text.strip()
        rank_index = seller_rank_text.find("#")
        rank_number = -1
        if rank_index != -1:
            space_index = seller_rank_text.find(" ", rank_index + 1)
            if space_index != -1:
                rank_number = seller_rank_text[rank_index + 1 : space_index]
                rank_number = rank_number.replace(",", "")

        # product description
        description_element = soup.find("div", id="productFactsDesktopExpander")
        if description_element:
            description = description_element.text.strip()

        # first image
        image_element = soup.select_one("#landingImage")
        first_image = image_element.attrs.get("src")

        image_result = requests.get(first_image)

        image_b64 = base64.b64encode(image_result.content)

        # convert all info to dictionary
        product_info = {
            "url": url,
            "product_name": product_name,
            "brand_name": brand_name,
            "price": price,
            "discount": discount,
            "rating_avg": rating_avg,
            "total_reviews": total_reviews,
            "rating_stars": rating_stars,
            "deal": deal,
            "free_delivery": free_delivery,
            "free_return": free_return,
            "amazon_choice": amazon_choice,
            "date_first_available": date_first_available,
            "rank_number": rank_number,
            "description": description,
            "first_image": image_b64.decode("utf-8"),
        }

        # convert dict to json
        json_str = json.dumps(product_info)

        return json_str
        # with open("product_info.json", "w") as outfile:
        # outfile.write(json_str)
