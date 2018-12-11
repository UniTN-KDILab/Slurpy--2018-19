#!/usr/bin/env python
# -*- coding: utf-8 -*-	
import json
import pandas
import numpy
import os

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
		
		firstpart = []
		
		i = 1
		for recipe in data:
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
			firstpart.append([id,label]+arr)
			i = i + 1
		
		size = len(firstpart[0])
		for col in range(2, size):
			try:
				occ = [row[col] for row in firstpart].count(True)
				if occ == in [1,2]:
					print("Deleting column "+str(col))
					for row in firstpart:
						del row[col]
					col = col - 1
			except:
				break
		
		print("Reduced from "+str(size-2)+" to "+str(len(firstpart[0])-2)+" attributes")
		
		print("Saving...")
		f_o = open(os.path.basename(__file__)+'.json', 'w')
		json.dump(firstpart, f_o, indent=4)
		f_o.close()
		print("Done.")
		

def rm_main():
	return convert()

if __name__ == '__main__':
	convert()