#!/usr/bin/env python
# -*- coding: utf-8 -*-	
import json
import pandas
import numpy

def convert():
	file_path = 'C:\\Users\\erry-\\Desktop\\kdi proj\\kdi-project-yes\\train.json'
	with open(file_path) as f:
		data = json.load(f)
		ingredients = []

		for recipe in data:
			ing = recipe.get("ingredients")
			for i in ing:
				if i not in ingredients:
					ingredients.append(i)
				
		print("Finished analyzing the stuff.")
		
		firstpart = pandas.DataFrame(columns=["id", "label"]+ingredients)
		tmp_arr = []
		
		pezzo = 4
		
		i = 1
		for recipe in data:
			if i > (pezzo - 1) * 10000:
				print("Recipe number "+str(i)+" of "+str(len(data)))
				id = recipe.get("id")
				label = recipe.get("cuisine")
				ing = recipe.get("ingredients")
				arr = []
				for ingredient in ingredients:
					if ingredient in ing:
						arr.append(True)
					else:
						arr.append(False)
				tmp_arr.append([id,label]+arr)
			if i == pezzo * 10000:
				break
			i = i + 1
		
		firstpart = pandas.concat([firstpart, pandas.DataFrame(tmp_arr, columns=["id", "label"]+ingredients)], copy=False, ignore_index=True, sort=False)
		return firstpart
		

def rm_main():
	return convert()

if __name__ == '__main__':
	convert()