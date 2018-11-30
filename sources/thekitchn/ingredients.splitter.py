import json
import re

data = []
units = []

def print_ingredients():
	splitted=[]
	i=1
	for row in data:
		if len(row) > 3:
			string_id = "tk"+str(i)
			ingridients_info = row[-1]
			for ingridient_info in ingridients_info:
				# print(ingridient_info[2])
				ing = re.findall('^[a-zA-Z0-9\s-]*',ingridient_info[2])[0]
				ing = ing.strip()
				splitted.append([string_id,ingridient_info[0],ingridient_info[1],ing])
			i = i + 1
	with open('thekitchn.ingredients.json', 'w') as outfile:
		json.dump(splitted, outfile)

if __name__ == '__main__':
	filename = 'thekitchn.scraper.py.json'
	unitsfile = 'units.json'
	with open(filename) as json_data:
		data = json.load(json_data,)
	with open(unitsfile) as json_units:
		units = json.load(json_units,)
	print_ingredients()