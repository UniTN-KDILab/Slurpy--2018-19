#!/usr/bin/env python
# -*- coding: utf-8 -*-	
import json
import pandas

def convert():
	file_path = 'C:\\Users\\erry-\\Desktop\\kdi proj\\kdi-project-yes\\sources\\whatscooking\\whatscooking.ingredients.json'
	with open(file_path) as f:
		data = json.load(f)
		return pandas.DataFrame(data, columns=["tmpID", "quantity", "unit", "ingredient"])

def rm_main():
	return convert()

if __name__ == '__main__':
	print(convert())