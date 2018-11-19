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

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.read()

def split_on_letter(s):
    match = re.compile("[^\W\d]").search(s)
    return s[:match.start()]
		
def getUrls(response):

	parser = html.fromstring(response)
	
	XPATH_LINKS = '//a[@class="wp-cpl-sc-thumba"]/@href'
	links = parser.xpath(XPATH_LINKS)
	return links

def ParseRicetta(response):
	parser = html.fromstring(response)
	
	XPATH_INGREDIENTS = '//li[@class="ingredient"]/text()'
	ingredients = parser.xpath(XPATH_INGREDIENTS)
	if not ingredients:
		return []
	
	XPATH_TITLE = '//h1[@class="entry-title"]/text()'
	title = parser.xpath(XPATH_TITLE)[0]
	
	XPATH_DESCRIPTION = '//div[@itemprop="description"]//text()'
	try:
		description = parser.xpath(XPATH_DESCRIPTION)[0]
	except:
		description = ""
	
	XPATH_SERVINGS = '//div[@itemprop="recipeYield"]//text()'
	servings = parser.xpath(XPATH_SERVINGS)
	try:
		servings = int(servings[0].split()[0])
	except:
		servings = -1
    
	cost = -1
	
	XPATH_TAGS = '//span[@itemprop="recipeCategory"]//text()'
	tags = parser.xpath(XPATH_TAGS)
	try:
		tags = tags[0].split(', ')
	except:
		tags = []
    
	XPATH_CALORIES = '//span[@itemprop="calories"]//text()'
	calories = parser.xpath(XPATH_CALORIES)
	try:
		calories = int(calories[0])
	except:
		calories = -1
	
	XPATH_FAT = '//span[@itemprop="fatContent"]//text()'
	fat = parser.xpath(XPATH_FAT)
	try:
		fat = float(split_on_letter(fat))
	except:
		fat = -1
	
	XPATH_CARBS = '//span[@itemprop="carbohydrateContent"]//text()'
	carbs = parser.xpath(XPATH_CARBS)
	try:
		carbs = float(split_on_letter(carbs))
	except:
		carbs = -1
	
	XPATH_FIBER = '//span[@itemprop="fiberContent"]//text()'
	fiber = parser.xpath(XPATH_FIBER)
	try:
		fiber = float(split_on_letter(fiber))
	except:
		fiber = -1
	
	XPATH_PROTEIN = '//span[@itemprop="proteinContent"]//text()'
	protein = parser.xpath(XPATH_PROTEIN)
	try:
		protein = float(split_on_letter(protein))
	except:
		protein = -1
	
	
	XPATH_DIRECTIONS = '//li[@itemprop="recipeInstructions"]//text()'
	directions = parser.xpath(XPATH_DIRECTIONS)
	directions = map((lambda x : x.replace('\u00a0','')), directions)
	directions = reduce((lambda x, y: x + " " + y), directions, "").split("\n")
	directions = list(filter(lambda x: x.strip() != "", directions))
		
	data = [title, description, servings, cost, calories, fat, carbs, fiber, protein, directions, ingredients, tags]
	
	return data
			
async def ReadUrls():
	baseUrl = ""
	maxPage = 1
	firstUrl = "https://www.ambitiouskitchen.com/recipes/bread/"
	
	urlsList = [firstUrl]
	#for i in range(1,(maxPage+1)):
	#	urlsList.append(firstUrl+"/page/"+str(i)+"/")
	n = len(urlsList)
	urls = []
	extracted_data = []
	
	tasks = []
	conn = aiohttp.TCPConnector(
        ssl=False
    )
	async with aiohttp.ClientSession(connector=conn) as session:
		for url in urlsList:
			tasks.append(fetch(session, url))
		htmls = await asyncio.gather(*tasks)
		i = 1
		n = len(htmls)
		for html in htmls:
			print("Analyzing page "+str(i)+" of "+str(n)+".")
			urls.extend([baseUrl + s for s in getUrls(html)])
			i = i + 1
		
		print("Analysis complete, processing now...")
		tasks = []
		
		for url in urls:
			tasks.append(fetch(session, url))
		htmls = await asyncio.gather(*tasks)
		i = 1
		n = len(htmls)
		for html in htmls:
			print("Processing page "+str(i)+" of "+str(n)+".")
			extracted_data.append(ParseRicetta(html))
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