import json
import re

data = []
units = []

def print_ingredients():
	splitted=[]
	i=1
	for row in data:
		string_id = "ep"+str(i)
		try:
			ingridients_info = row["ingredients"]
			for ingridient_info in ingridients_info:
				first_part = ingridient_info.encode('ascii', 'ignore')
				first_part = first_part.decode("utf-8")
				#print(first_part)
				parentesi = "\(.*\)\s"
				par = re.findall(parentesi,first_part)
				for p in par:
					first_part= first_part.replace(p,"")
				garbage = "\s.*\(*-\w*"
				gar = re.findall(garbage,first_part)
				for g in gar:
					first_part= first_part.replace(g,"")

				first_part = re.findall('^[a-zA-Z0-9/()%/\\".\s-]*', first_part)[0]

				regex_word = r"\b[^\d\W]+\b"


				u=[]
				q = re.findall(r"[0-9/]+-*[0-9]*\s",first_part)
				if len(q)>0:
					#print(first_part)
					u = re.findall(regex_word,first_part)[0]
					if u not in units:
						u = []

				for qq in q:
					first_part = first_part.replace(qq,"")
				if len(u)>0:
					first_part = first_part.replace(u,"")

				ing = re.findall('^[a-zA-Z0-9\s-]*',first_part)[0]
				ing = ing.strip()
				str_q = ' '.join(q)
				str_q=str_q.strip()
				str_q=re.sub(' +',' ',str_q)
				splitted.append([string_id,str_q,u,ing])
				i=i+1
		except:
			i=i
	with open('epicurus.ingredients.json', 'w') as outfile:
		json.dump(splitted, outfile)

if __name__ == '__main__':
	filename = 'formatted_recipes.json'
	unitsfile = 'units.json'
	with open(filename) as json_data:
		data = json.load(json_data,)
	with open(unitsfile) as json_units:
		units = json.load(json_units,)
	print_ingredients()
