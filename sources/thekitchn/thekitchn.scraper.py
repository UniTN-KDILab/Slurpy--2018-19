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

async def fetch(session, url, i=0, n=0):
	async with session.get(url) as response:
		if n != 0:
			print("Processing page "+str(i)+" of "+str(n)+".")
		return await response.read()

async def fetch_post(session, url, json):
    async with session.post(url, json=json) as response:
        return await response.read()
		
def getUrls(response):

	parser = html.fromstring(response)
	
	XPATH_LINKS = '//a[@class="SearchTeaser__wrapping-link"]/@href'
	links = parser.xpath(XPATH_LINKS)
	
	return links

def ParseRicetta(response):
	parser = html.fromstring(response)
	
	XPATH_TITLE = '//h1/text()'
	try:
		title = parser.xpath(XPATH_TITLE)[0]
	except:
		return []
	#	XPATH_TITLE = '//h1[@class="Post__headline"]/text()'
	#	title = parser.xpath(XPATH_TITLE)[0]
	
	# JSON.parse($x('//div[@id="__next-error"]/../script/text()')[0].textContent.slice(27,-400))
	# props.serverState.apollo.data
	#
	# $RecipeBundleItem_*.data.nutritionalGuide -> servings, calories (to be divided)
	# $RecipeBundleItem_*.data.nutritionalGuide.primaryNutrients.0 (to 6) (fat, saturated, carbs, fibers, sugar, protein, sodium) (.quantity (e da modificare in numero))
	# $RecipeBundleItem_*.data.nutritionalGuide -> labels.json

	XPATH_SCRIPT = '//div[@id="__next-error"]/../script/text()'
	XPATH_JSON = '//div[@data-render-react-id="recipes/Recipe"]/@data-props'
	try:
		script = parser.xpath(XPATH_SCRIPT)[0]
		script = script.strip().split("\n")[0].split("=",1)[1].strip()
		script = json.loads(script)
		script = script.get("props").get("serverState").get("apollo").get("data")
		script = [(key.split(".")[-1], value) for key, value in script.items() if key.startswith("$RecipeBundleItem_")]
		nutritionalGuide = [el[1] for el in script if el[0] == "nutritionalGuide"][0]
	
		servings = nutritionalGuide.get("servings")
		calories = int(nutritionalGuide.get("calories") / servings)
		labels = nutritionalGuide.get("labels").get("json")
	
		fat = [el[1] for el in script if el[0] == "0"][0]
		fat = float(fat.get("quantity").split()[0])
	
		saturated = [el[1] for el in script if el[0] == "1"][0]
		saturated = float(saturated.get("quantity").split()[0])
	
		carbs = [el[1] for el in script if el[0] == "2"][0]
		carbs = float(carbs.get("quantity").split()[0])
	
		fibers = [el[1] for el in script if el[0] == "3"][0]
		fibers = float(fibers.get("quantity").split()[0])
	
		sugar = [el[1] for el in script if el[0] == "4"][0]
		sugar = float(sugar.get("quantity").split()[0])
	
		protein = [el[1] for el in script if el[0] == "5"][0]
		protein = float(protein.get("quantity").split()[0])
	
		sodium = [el[1] for el in script if el[0] == "6"][0]
		sodium = float(sodium.get("quantity").split()[0])
	except:
		try:
			script = parser.xpath(XPATH_JSON)[0]
			script = json.loads(script)
			script = script.get("nutritional_guide")
	
			servings = script.get("servings")
			calories = int(script.get("calories") / servings)
			labels = script.get("labels")
	
			fat = [el for el in script.get("primary_nutrients") if el.get("label") == "Fat"][0]
			fat = float(fat.get("quantity").split()[0])
	
			saturated = [el for el in script.get("primary_nutrients") if el.get("label") == "Saturated"][0]
			saturated = float(saturated.get("quantity").split()[0])
	
			carbs = [el for el in script.get("primary_nutrients") if el.get("label") == "Carbs"][0]
			carbs = float(carbs.get("quantity").split()[0])
	
			fibers = [el for el in script.get("primary_nutrients") if el.get("label") == "Fiber"][0]
			fibers = float(fibers.get("quantity").split()[0])
	
			sugar = [el for el in script.get("primary_nutrients") if el.get("label") == "Sugars"][0]
			sugar = float(sugar.get("quantity").split()[0])
	
			protein = [el for el in script.get("primary_nutrients") if el.get("label") == "Protein"][0]
			protein = float(protein.get("quantity").split()[0])
	
			sodium = [el for el in script.get("primary_nutrients") if el.get("label") == "Sodium"][0]
			sodium = float(sodium.get("quantity").split()[0])
		except:
			servings = -1
			calories = -1
			labels = []
			fat = -1
			saturated = -1
			carbs = -1
			fibers = -1
			sugar = -1
			protein = -1
			sodium = -1
	
	XPATH_DESCRIPTION = '//div[contains(@class, "Post__item") and contains(@class, "Post__html")]//p//text()'
	description = parser.xpath(XPATH_DESCRIPTION)
	description = list(map((lambda x : x.replace('\n','')), description))
	description = reduce((lambda x, y: x + "<br>" + y), description, "")
	
	cost = -1
	
	XPATH_DIRECTIONS = '//*[@itemprop="recipeInstructions"]//text()'
	directions = parser.xpath(XPATH_DIRECTIONS)
	
	XPATH_INGREDIENTS_THREE = '//*[@itemprop="recipeIngredient"][count(span)=3]//span|p[text()]'
	ingredients_three = parser.xpath(XPATH_INGREDIENTS_THREE)
	ingredients_three = list(map(lambda x: x.text_content(), ingredients_three))
	ingredients_three = list(filter(lambda x: x.strip() != "", ingredients_three))
	
	XPATH_INGREDIENTS_TWO = '//*[@itemprop="recipeIngredient"][count(span)=2]//span|p[text()]'
	ingredients_two = parser.xpath(XPATH_INGREDIENTS_TWO)
	ingredients_two = list(map(lambda x: x.text_content(), ingredients_two))
	ingredients_two = list(filter(lambda x: x.strip() != "", ingredients_two))
	
	XPATH_INGREDIENTS_ONE = '//*[@itemprop="recipeIngredient"][count(span)=1]//text()'
	ingredients_one = parser.xpath(XPATH_INGREDIENTS_ONE)
	ingredients_one = list(filter(lambda x: x.strip() != "", ingredients_one))
	
	ingredients = []
	for i in range(0, len(ingredients_three), 3):
		try:
			ingredients.append([ingredients_three[i].strip(), ingredients_three[i+1].strip(), ingredients_three[i+2].strip()])
		except:
			print(ingredients_three)
	
	for i in range(0, len(ingredients_two), 2):
		try:
			ingredients.append([ingredients_two[i].strip(), "", ingredients_two[i+1].strip()])
		except:
			print(ingredients_two) # https://www.thekitchn.com/how-to-make-a-fool-proof-quiche-168459 !!!!!
	
	for ing in ingredients_one:
		ingredients.append(["", "", ing.strip()])
		
	data = [title, description, servings, cost, calories, fat, saturated, carbs, fibers, sugar, protein, sodium, directions, ingredients]
	
	return data
			
async def ReadUrls():
	url = 'https://bzshv0ttwo-dsn.algolia.net/1/indexes/*/queries?x-algolia-application-id=BZSHV0TTWO&x-algolia-api-key=10a4cda1d1aa4f08c2f2cc94ed0c5648'
	extracted_data = []
	
	tasks = []
	async with aiohttp.ClientSession() as session:
		tasks = []
		
		for i in range(10):
			tasks.append(fetch_post(session, url, {"requests":[{"indexName":"FauxRecipes","params":"query=-&tagFilters=%5B%22Kitchn%22%5D&page="+str(i)+"&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetFilters=%5B%22search_categories%3ARecipe%22%5D&facets=%5B%5D"}]}))
		
		jsons = await asyncio.gather(*tasks)
		
		print("Analysis complete, processing now...")
		tasks = []
		
		for index, el in enumerate(jsons):
			for i in range(100):
				url = json.loads(el).get("results")[0].get("hits")[i].get("path")
				tasks.append(fetch(session, "https://www.thekitchn.com/"+url, 100*index+i+1, 1000))
		htmls = await asyncio.gather(*tasks)
		for html in htmls:
		 	extracted_data.append(ParseRicetta(html))
		
		
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