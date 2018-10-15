#!/usr/bin/env python
# -*- coding: utf-8 -*-	
from lxml import html  
import json
import requests
import json,re
from dateutil import parser as dateparser
from time import sleep
from functools import reduce
import numpy as np
import pandas
import asyncio

def getUrls(url):
	headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
	page = requests.get(url,headers = headers,verify=False)
	page_response = page.text

	parser = html.fromstring(page_response)
	
	XPATH_LINKS = '//a[@rel="bookmark"]/@href'
	links = parser.xpath(XPATH_LINKS)
	
	return links

async def ParseRicetta(url):
	headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
	page = requests.get(url,headers = headers,verify=False)
	page_response = page.text

	parser = html.fromstring(page_response)
	
	XPATH_TITLE = '//h1/text()'
	title = parser.xpath(XPATH_TITLE)[0]
	
	XPATH_DIRECTIONS = '//div[@property="schema:instructions"]//text()'
	directions_tmp = parser.xpath(XPATH_DIRECTIONS)
	#directions_tmp = Replacer(directions_tmp, ["\u00a0", "\n"], ["", "<br />"])
	directions_tmp = map((lambda x : x.replace('\u00a0','').replace('\n','<br />')), directions_tmp)
	directions = reduce((lambda x, y: x + y), directions_tmp)
	
	XPATH_INGREDIENTS_QUANTITIES = '//span[@class="quantity-unit"]/text()'
	ingredients_quantities = parser.xpath(XPATH_INGREDIENTS_QUANTITIES)
	#ingredients_quantities = Replacer(ingredients_quantities, ["\u00a0", "\u00ad"], ["", ""])
	ingredients_quantities = list(map((lambda x : x.replace('\u00a0','').replace('\u00ad','')), ingredients_quantities))
	
	XPATH_INGREDIENTS_NAMES = '//span[@class="ingredient-name"]/text()'
	ingredients_names = parser.xpath(XPATH_INGREDIENTS_NAMES)
	#ingredients_names = Replacer(ingredients_names, ["\u00a0", "\u00ad"], ["", ""])
	ingredients_names = list(map((lambda x : x.replace('\u00a0','').replace('\u00ad','')), ingredients_names))
	
	XPATH_INGREDIENTS_FREE = '//span[@class="free-label"]/text()'
	ingredients_free = parser.xpath(XPATH_INGREDIENTS_FREE)
	#ingredients_free = Replacer(ingredients_free, ["\u00a0", "\u00ad"], ["", ""])
	ingredients_free = list(map((lambda x : x.replace('\u00a0','').replace('\u00ad','')), ingredients_free))
	
	ingredients = []
	i = 0
	for quant in ingredients_quantities:
		ingredients.append([quant.strip(), ingredients_names[i].strip()])
		i = i + 1
	
	for item in ingredients_free:
		ingredients.append(["", item.strip()])
	'''
	XPATH_REVIEW_SECTION_1 = '//div[contains(@id,"reviews-summary")]'
	XPATH_REVIEW_SECTION_2 = '//div[@data-hook="review"]'

	XPATH_AGGREGATE_RATING = '//table[@id="histogramTable"]//tr'
	XPATH_PRODUCT_NAME = '//h1//span[@id="productTitle"]//text()'
	XPATH_PRODUCT_PRICE  = '//span[@id="priceblock_ourprice"]/text()'
	
	raw_product_price = parser.xpath(XPATH_PRODUCT_PRICE)
	product_price = ''.join(raw_product_price).replace(',','')

	raw_product_name = parser.xpath(XPATH_PRODUCT_NAME)
	product_name = ''.join(raw_product_name).strip()
	total_ratings  = parser.xpath(XPATH_AGGREGATE_RATING)
	reviews = parser.xpath(XPATH_REVIEW_SECTION_1)
	if not reviews:
		reviews = parser.xpath(XPATH_REVIEW_SECTION_2)
	ratings_dict = {}
	reviews_list = []
	
	if not reviews:
		raise ValueError('unable to find reviews in page')

	#grabing the rating  section in product page
	for ratings in total_ratings:
		extracted_rating = ratings.xpath('./td//a//text()')
		if extracted_rating:
			rating_key = extracted_rating[0] 
			raw_raing_value = extracted_rating[1]
			rating_value = raw_raing_value
			if rating_key:
				ratings_dict.update({rating_key:rating_value})
	
	#Parsing individual reviews
	for review in reviews:
		XPATH_RATING  = './/i[@data-hook="review-star-rating"]//text()'
		XPATH_REVIEW_HEADER = './/a[@data-hook="review-title"]//text()'
		XPATH_REVIEW_POSTED_DATE = './/span[@data-hook="review-date"]//text()'
		XPATH_REVIEW_TEXT_1 = './/div[@data-hook="review-collapsed"]//text()'
		XPATH_REVIEW_TEXT_2 = './/div//span[@data-action="columnbalancing-showfullreview"]/@data-columnbalancing-showfullreview'
		XPATH_REVIEW_COMMENTS = './/span[@data-hook="review-comment"]//text()'
		XPATH_AUTHOR  = './/span[contains(@class,"profile-name")]//text()'
		XPATH_REVIEW_TEXT_3  = './/div[contains(@id,"dpReviews")]/div/text()'
		
		raw_review_author = review.xpath(XPATH_AUTHOR)
		raw_review_rating = review.xpath(XPATH_RATING)
		raw_review_header = review.xpath(XPATH_REVIEW_HEADER)
		raw_review_posted_date = review.xpath(XPATH_REVIEW_POSTED_DATE)
		raw_review_text1 = review.xpath(XPATH_REVIEW_TEXT_1)
		raw_review_text2 = review.xpath(XPATH_REVIEW_TEXT_2)
		raw_review_text3 = review.xpath(XPATH_REVIEW_TEXT_3)

		#cleaning data
		author = ' '.join(' '.join(raw_review_author).split())
		review_rating = ''.join(raw_review_rating).replace('out of 5 stars','')
		review_header = ' '.join(' '.join(raw_review_header).split())

		try:
			review_posted_date = dateparser.parse(''.join(raw_review_posted_date)).strftime('%d %b %Y')
		except:
			review_posted_date = None
		review_text = ' '.join(' '.join(raw_review_text1).split())

		#grabbing hidden comments if present
		if raw_review_text2:
			json_loaded_review_data = json.loads(raw_review_text2[0])
			json_loaded_review_data_text = json_loaded_review_data['rest']
			cleaned_json_loaded_review_data_text = re.sub('<.*?>','',json_loaded_review_data_text)
			full_review_text = review_text+cleaned_json_loaded_review_data_text
		else:
			full_review_text = review_text
		if not raw_review_text1:
			full_review_text = ' '.join(' '.join(raw_review_text3).split())

		raw_review_comments = review.xpath(XPATH_REVIEW_COMMENTS)
		review_comments = ''.join(raw_review_comments)
		review_comments = re.sub('[A-Za-z]','',review_comments).strip()
		review_dict = {
							'review_comment_count':review_comments,
							'review_text':full_review_text,
							'review_posted_date':review_posted_date,
							'review_header':review_header,
							'review_rating':review_rating,
							'review_author':author

						}
		reviews_list.append(review_dict)
	'''
	data = [url, title, directions, ingredients]
	#await asyncio.sleep(15)
	return data
			
def ReadUrls():
	urls = getUrls("https://whatscooking.fns.usda.gov/search/recipes")
	baseUrl = "https://whatscooking.fns.usda.gov"
	#print(urls)
	#UrlsList = ['https://whatscooking.fns.usda.gov/recipes/food-distribution-fdd/15-minute-enchiladas', 'https://whatscooking.fns.usda.gov/recipes/food-distribution-fdd/15-minute-enchiladas']
	extracted_data = []
	loop = asyncio.get_event_loop()
	for url in urls:
		print("Downloading and processing page "+url)
		extracted_data.append(loop.run_until_complete(ParseRicetta(baseUrl+url)))
	loop.close()
	f = open('data.json','w')
	json.dump(extracted_data,f,indent=4)
	#return pandas.DataFrame(extracted_data)
	return pandas.DataFrame(extracted_data, columns=["url", "title", "directions", "ingredients"])
	#return pandas.DataFrame([["a", "b", "c", "d"],["a", "b", "c", "d"]], columns=["a", "b", "c", "d"])

def rm_main():
	return ReadUrls()

if __name__ == '__main__':
	ReadUrls()