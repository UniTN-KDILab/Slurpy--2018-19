#!/usr/bin/env python
# -*- coding: utf-8 -*-	
import json
import pandas
import numpy as np
import Levenshtein

def levenshtein(source, target):
    if len(source) < len(target):
        return levenshtein(target, source)

    # So now we have len(source) >= len(target).
    if len(target) == 0:
        return len(source)

    # We call tuple() to force strings to be used as sequences
    # ('c', 'a', 't', 's') - numpy uses them as values by default.
    source = np.array(tuple(source))
    target = np.array(tuple(target))

    # We use a dynamic programming algorithm, but with the
    # added optimization that we only need the last two rows
    # of the matrix.
    previous_row = np.arange(target.size + 1)
    for s in source:
        # Insertion (target grows longer than source):
        current_row = previous_row + 1

        # Substitution or matching:
        # Target and source items are aligned, and either
        # are different (cost of 1), or are the same (cost of 0).
        current_row[1:] = np.minimum(
                current_row[1:],
                np.add(previous_row[:-1], target != s))

        # Deletion (target grows shorter than source):
        current_row[1:] = np.minimum(
                current_row[1:],
                current_row[0:-1] + 1)

        previous_row = current_row

    return previous_row[-1]

def convert():
	ingredients = []
	file_path = 'C:\\Users\\erry-\\Desktop\\kdi proj\\kdi-project-yes\\train.json'
	with open(file_path) as f:
		data = json.load(f)

		for recipe in data:
			ing = recipe.get("ingredients")
			for i in ing:
				if i not in ingredients:
					ingredients.append(i)
	
	print("Done with list.")
	
	pezzo = 3
	
	recipes = {}
	file_path = 'C:\\Users\\erry-\\Desktop\\kdi proj\\kdi-project-yes\\sources\\epicurious\\epicurious.ingredients.json'
	with open(file_path) as f:
		data = json.load(f)
		data = list(map(lambda x: [x[0],x[3]], data))	
		
		n = len(data)
		i = 1
		big_number = len(ingredients)
		first_id = (pezzo - 1) * 10000 + 1
		last_id = pezzo * 10000
		for ingredient in data:
			#if int(ingredient[0][2:]) == last_id:
			#	break
			#if int(ingredient[0][2:]) >= first_id:
			if int(ingredient[0][2:]) in [10000, 20000]:
				if ingredient[0] not in recipes:
					recipes[ingredient[0]] = [False] * big_number
				print(str(i)+"/"+str(n))
				best = ""
				lev = list(map(lambda x: Levenshtein.distance(x, ingredient[1]), ingredients))
				if np.amin(lev) <= 5:
					ind = np.argmin(lev)
					recipes[ingredient[0]][ind] = True
			i = i + 1
	
	final_data = []
	for k,v in recipes.items():
		final_data.append([k, ""]+v)
	return pandas.DataFrame(final_data, columns=["id", "label"]+ingredients)

def rm_main():
	return convert()

if __name__ == '__main__':
	print(convert())