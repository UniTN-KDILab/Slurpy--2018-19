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

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.read()

def getUrls(response):

	parser = html.fromstring(response)
	
	XPATH_LINKS = '//a[@rel="bookmark"]/@href'
	links = parser.xpath(XPATH_LINKS)
	
	return links

def ParseRicetta(response):
	parser = html.fromstring(response)
	
	XPATH_TITLE = '//h1/text()'
	title = parser.xpath(XPATH_TITLE)[0]
	
	XPATH_DESCRIPTION = '//div[@property="schema:summary"]//text()'
	description = parser.xpath(XPATH_DESCRIPTION)
	description = map((lambda x : x.replace('\u00a0','').replace('\n','')), description)
	description = reduce((lambda x, y: x + y), description, "")
	
	XPATH_SERVINGS = '//div[@class="r_summary_block"]/div/text()'
	servings_tmp = parser.xpath(XPATH_SERVINGS)[0]
	servings = int(servings_tmp.split()[0])
	
	XPATH_NOTDOLLARO = 'count(//span[contains(@class, "fa-usd") and contains(@class, "inactive")])'
	notdollaro = parser.xpath(XPATH_NOTDOLLARO)
	XPATH_ALLDOLLARO = 'count(//span[contains(@class, "fa-usd")])'
	alldollaro = parser.xpath(XPATH_ALLDOLLARO)
	if alldollaro:
		cost = 100 * (1 - notdollaro/alldollaro)
	else:
		cost = 0
	
	XPATH_CALORIES = '//div[@class="k_panel"]/div[contains(@class ,"np_row_field_total_calories_final")]/div[2]/text()'
	calories = parser.xpath(XPATH_CALORIES)
	try:
		calories = int(calories[0])
	except (ValueError, IndexError) as e:
		calories = 0
	
	XPATH_FAT = '//div[@class="k_panel"]/div[contains(@class ,"np_row_field_total_fat_final")]/div[2]/text()'
	fat = parser.xpath(XPATH_FAT)
	try:
		fat = float(fat[0].split()[0])
	except (ValueError, IndexError) as e:
		fat = 0
	
	XPATH_PROTEIN = '//div[@class="k_panel"]/div[contains(@class ,"np_row_field_protein")]/div[2]/text()'
	protein = parser.xpath(XPATH_PROTEIN)
	try:
		protein = float(protein[0].split()[0])
	except (ValueError, IndexError) as e:
		protein = 0
	
	XPATH_SODIUM = '//div[@class="k_panel"]/div[contains(@class ,"np_row_field_sodium")]/div[2]/text()'
	sodium = parser.xpath(XPATH_SODIUM)
	try:
		sodium = float(sodium[0].split()[0])
	except (ValueError, IndexError) as e:
		sodium = 0
	
	XPATH_DIRECTIONS = '//div[@property="schema:instructions"]//text()'
	directions_tmp = parser.xpath(XPATH_DIRECTIONS)
	directions_tmp = map((lambda x : x.replace('\u00a0','')), directions_tmp)
	directions_tmp = reduce((lambda x, y: x + y), directions_tmp, "").split("\n")
	directions = list(filter(lambda x: x.strip() != "", directions_tmp))
	
	XPATH_INGREDIENTS_QUANTITIES = '//span[@property="schema:amount"]//text()'
	ingredients_quantities = parser.xpath(XPATH_INGREDIENTS_QUANTITIES)
	ingredients_quantities = list(map((lambda x : x.replace('\u00a0','').replace('\u00ad','')), ingredients_quantities))
	
	XPATH_INGREDIENTS_NAMES = '//span[@property="schema:name"]//text()'
	ingredients_names = parser.xpath(XPATH_INGREDIENTS_NAMES)
	ingredients_names = list(map((lambda x : x.replace('\u00a0','').replace('\u00ad','')), ingredients_names))
	
	XPATH_INGREDIENTS_FREE = '//span[@class="free-label"]//text()'
	ingredients_free = parser.xpath(XPATH_INGREDIENTS_FREE)
	ingredients_free = list(map((lambda x : x.replace('\u00a0','').replace('\u00ad','')), ingredients_free))
	
	ingredients = []
	i = 0
	for quant in ingredients_quantities:
		ingredients.append([quant.strip(), ingredients_names[i].strip()])
		i = i + 1
	
	for item in ingredients_free:
		ingredients.append(["", item.strip()])
		
	data = [title, description, servings, cost, calories, fat, protein, sodium, directions, ingredients]
	
	return data
			
async def ReadUrls():
	baseUrl = "https://whatscooking.fns.usda.gov"
	maxPage = 76
	firstUrl = "https://whatscooking.fns.usda.gov/search/recipes"
	
	urlsList = [firstUrl]
	for i in range(1,(maxPage+1)):
		urlsList.append(firstUrl+"?page="+str(i))
	n = len(urlsList)
	urls = []
	extracted_data = []
	
	tasks = []
	async with aiohttp.ClientSession() as session:
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