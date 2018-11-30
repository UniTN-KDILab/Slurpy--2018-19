#!/usr/bin/env python
# -*- coding: utf-8 -*-	
import json
import pandas

def convert():
	file_path = 'C:\\Users\\erry-\\Desktop\\kdi proj\\kdi-project-yes\\sources\\whatscooking\\whatscooking.recipes.scraper.py.json'
	with open(file_path) as f:
		data = json.load(f)
		i = 1
		for recipe in data:
			recipe.insert(0,"wc"+str(i))
			i = i + 1
		return pandas.DataFrame(data, columns=["tmpID", "title", "description", "servings", "cost (0-100)", "calories", "fat (g)", "protein (g)", "sodium (mg)", "directions", "ingredients"])

def rm_main():
	return convert()

if __name__ == '__main__':
	print(convert())