import json
import re
import pandas

def rm_main():
	file_path = 'C:\\Users\\erry-\\Desktop\\kdi proj\\kdi-project-yes\\sources\\epicurious\\epicurious.ingredients.json'
	with open(file_path) as f:
		data = json.load(f)
		return pandas.DataFrame(data, columns=["tmpID", "quantity", "unit", "ingredient"])
