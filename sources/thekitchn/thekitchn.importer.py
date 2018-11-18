#!/usr/bin/env python
# -*- coding: utf-8 -*-	
import json
import pandas

def convert():
	file_path = 'C:\\Users\\erry-\\Desktop\\kdi proj\\kdi-project-yes\\thekitchn.scraper.py.json'
	with open(file_path) as f:
		data = json.load(f)
		data = list(filter(lambda x: len(x) > 3, data))
		return pandas.DataFrame(data, columns=["title", "description", "servings", "cost (0-100)", "calories", "fat (g)", "saturated (g)", "carbs (g)", "fiber (g)", "sugar (g)", "protein (g)", "sodium (mg)", "directions", "ingredients"])

def rm_main():
	return convert()

if __name__ == '__main__':
	print(convert())