#!/usr/bin/env python
# -*- coding: utf-8 -*-	
import json
import pandas

def convert():
	file_path = 'C:\\Users\\erry-\\Desktop\\kdi proj\\kdi-project-yes\\sources\\webdm\\webdm.recipes.scraper.py.json'
	with open(file_path) as f:
		data = json.load(f)
		return pandas.DataFrame(data, columns=["title", "description", "servings", "cost (0-100)", "calories", "fat (g)", "protein (g)", "sodium (mg)", "directions", "ingredients", "tags"])

def rm_main():
	return convert()

if __name__ == '__main__':
	print(convert())