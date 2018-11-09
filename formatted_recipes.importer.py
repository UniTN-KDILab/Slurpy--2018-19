#!/usr/bin/env python
# -*- coding: utf-8 -*-	
import json
import pandas

def convert():
	file_path = 'C:\\Users\\erry-\\Desktop\\kdi proj\\kdi-project-yes\\formatted_recipes.json'
	with open(file_path) as f:
		data = json.load(f)
		formatted_data = []
		for recipe in data:
			title = recipe.get("title", "").strip()
			if(title):
				description = recipe.get("desc", "")
				if description:
					description = description.replace('\n','')
				servings = -1
				cost = -1
				calories = recipe.get("calories")
				fat = recipe.get("fat")
				protein = recipe.get("protein")
				sodium = recipe.get("sodium")
				directions = recipe.get("directions")
				ingredients = recipe.get("ingredients")
			
				formatted_data.append([title, description, servings, cost, calories, fat, protein, sodium, directions, ingredients])
		
		return pandas.DataFrame(formatted_data, columns=["title", "description", "servings", "cost (0-100)", "calories", "fat (g)", "protein (g)", "sodium (mg)", "directions", "ingredients"])

def rm_main():
	return convert()

if __name__ == '__main__':
	print(convert())