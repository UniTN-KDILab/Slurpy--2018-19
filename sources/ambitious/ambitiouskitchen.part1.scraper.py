#!/usr/bin/env python
# -*- coding: utf-8 -*-	
from lxml import html  
import json
import asyncio
import aiohttp
import json,re
from dateutil import parser as dateparser
from time import sleep
from functools import reduce
import numpy as np
import pandas
import urllib3
import os
import socket
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.read()
		
def getUrls(response):

	parser = html.fromstring(response)
	
	XPATH_LINKS = '//a[@class="wp-cpl-sc-thumba"]/@href'
	links = parser.xpath(XPATH_LINKS)
	return links
			
async def ReadUrls():
	baseUrl = "https://www.ambitiouskitchen.com/recipes/"
	# maxPage = 1
	endpoints = ["appetizers", "bread", "breakfast", "brownies-bars", "burgers", "cake", "cobblers-crisps-crumbles", "condiments-sauces-butters", "cookies", "cupcakes", "dairy-free", "doughnuts", "fall", "favorites", "fish", "gluten-free", "grain-free", "under-400-calories", "high-protein-snacks", "ice-cream-frozen-yogurt", "low-fat", "muffin-scones", "paleo", "pancakes-waffles", "pasta", "pie", "pizza", "poultry", "salads", "sandwitches-wraps", "smoothies-shakes-drinks", "side-dish-vegetables", "soups-stews", "spring", "summer", "sweets-under-200-calories", "vegan", "vegetarian", "winter"]
	# firstUrl = "https://www.ambitiouskitchen.com/recipes/bread/"
	
	# urlsList = [firstUrl]
	# for i in range(1,(maxPage+1)):
	#	urlsList.append(firstUrl+"/page/"+str(i)+"/")
	n = len(endpoints)
	urls = []
	extracted_data = []
	
	tasks = []
	async with aiohttp.ClientSession() as session:
		for url in endpoints:
			tasks.append(fetch(session, baseUrl + url + "/"))
		htmls = await asyncio.gather(*tasks)
		i = 1
		n = len(htmls)
		for html in htmls:
			print("Analyzing page "+str(i)+" of "+str(n)+".")
			urls.extend([s for s in getUrls(html)])
			i = i + 1
		
		print("Saving...")
		f = open(os.path.basename(__file__)+'.json', 'w')
		json.dump(extracted_data, f, indent=4)
		f.close()
		print("Done.")
	
	
	# return pandas.DataFrame(extracted_data, columns=["title", "description", "servings", "cost (0-100)", "calories", "fat (g)", "protein (g)", "sodium (mg)", "directions", "ingredients"])

if __name__ == '__main__':
	#Declare event loop
	loop = asyncio.get_event_loop()
	#Run the code until completing all task
	loop.run_until_complete(ReadUrls())
	#Close the loop
	loop.close()