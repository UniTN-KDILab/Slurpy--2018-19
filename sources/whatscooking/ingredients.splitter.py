import json
import re

data = []
unit_exp = []

def print_ingredients():
	splitted=[]
	i = 1
	for row in data:
		ingridients_info = row[9]
		string_id="wc"+str(i)
		for ingridient_info in ingridients_info:
			units = ingridient_info[0]
			#for unit in units:
			regex_word = r"\b[^\d\W]+\b"
			u = re.findall(regex_word,units)
			q = re.findall(r"[0-9/]+",units)
			ing = ingridient_info[1]
			ing = re.findall('^[a-zA-Z0-9\s]*',ing)[0]
			ing = ing.strip()
			
			str_q = ' '.join(q)
			str_q=str_q.strip()
			str_q=re.sub(' +',' ',str_q)
					
			splitted.append([string_id,str_q,u,ing])
			if u not in unit_exp:
				unit_exp.append(u)
		i = i+1
	with open('whatscooking.ingredients.json', 'w') as outfile:
		json.dump(splitted, outfile)
	with open('units.json', 'w') as outfile2:
		json.dump(unit_exp, outfile2)

if __name__ == '__main__':
	filename = 'whatscooking.recipes.scraper.py.json'
	with open(filename) as json_data:
		data = json.load(json_data,)
	print_ingredients()