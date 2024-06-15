# Auxillary features (for retrieving, images comments, sentiment, etc. )
import requests
from bs4 import BeautifulSoup
import re
import json
import asyncio

class ItemDetailedViewScrape:
    
    # RETURNS LIST CONTAINING URLS
    async def retrieve_image_url(self, item_url):
        custom_headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
            "accept-language": "en-US,en;q=0.5",
        }
        response = requests.get(item_url, headers=custom_headers)
        if response.status_code != 200:
            print("Cannot access")
            exit()
        soup = BeautifulSoup(response.text, 'lxml')

        # print(soup)
        # Find the script tag containing "ImageBlockATF"
        script_tag = soup.find('script', string=lambda string: string and 'ImageBlockATF' in string)

        # extract js code from the script tag
        text = script_tag.text

        text = text.split("main\":")[1]
        text = text.split(",\"variant")[0]
        text.strip()
        data = json.loads(text)
        urls = list(data.keys())

        print(urls)
        return urls



async def testImgRetrieve():
    await ItemDetailedViewScrape().retrieve_image_url("https://www.amazon.com/Trucks-Front-Bumper-Assembly-25-SJ04/dp/B07Z87FHG3/ref=sr_1_1?dib=eyJ2IjoiMSJ9.nVDbpSY0kbOJzcgBPAkC3S4d5bSRcBAy2eLBCm356RbaYASkuyW67cPG5dopz5STaEeB6_FREdXpT9woDI1k50T-c4LaOG_hnEdfChm4N4ngSIi4F6R8di2ucd2UfrGEFBLVdVHil7CYFXXtAY5kd8sf5buYCDodbcoKPmhnJsPnHNg7sB93fhz8OnkOePcyBM5qur3unHGuBKCcdZmagu6f7pjUvAaSczra4lds3MDSIwcc2JVbdRU34Zinr6HXgfh8Bn9BBl8aqJ5lEgV7bJAJ8AmEU7GM-Tx1fqGqMl0.So6C_U8pGADTdP0Or14GHthPLfFI9c8cIXzCA5G4-oc&dib_tag=se&keywords=RC+car+hood+bumper&qid=1718320394&sr=8-1")


asyncio.run(testImgRetrieve())



        
