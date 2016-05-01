#!/usr/bin/python
import csv, codecs, json, re, sys

reload(sys)
sys.setdefaultencoding("UTF-8")

def word_count(string):
	word_list = re.findall(r"[\w']+", string)
	return len(word_list)
	
def paragraph_count(string):
	#paragraph_count = re.findall(r"<br>|<br/>|</p>", string)
	return 0	

def h1_count(string):
	return 0

def h2_count(string):
	return 0

def h3_count(string):
	return 0

def list_count(string):
	return 0

def table_count(string):
	return 0

def image_count(string):
	return 0

def list_broken(string):
	return 0

def table_broken(string):
	return 0

def image_broken(string):
	return 0

def space_broken(string):
	return 0
	
def get_field(field, row):
	if field in row['fields']:
		return row['fields'][field][0]
	else:
		return ''

def calculate_stats(data):
	stats = []
	for row in data:
		topText = get_field('shortText', row)
		leftText = get_field('sideText', row)
		bottomText = get_field('text', row)
		
		url = get_field('url', row)
		if url:
			product = 'shop'
		else:
			url = get_field('store.url', row)
			product = 'coupon'
		
		if not topText and not bottomText and not leftText:
			print "hallo"
			continue
		
		stat = {}
		stat['url'] = url
		stat['product'] = product
		stat['brand'] = get_field('source.brand', row)
		stat['series'] = get_field('source.series', row)
		stat['model'] = get_field('source.model', row)
		stat['category'] = get_field('source.category', row)
		stat['gender'] = get_field('source.gender', row)
		stat['color'] = get_field('source.color', row)
		
		stat['Top_Words'] = word_count(topText)
		stat['Left_Words'] = word_count(leftText)
		stat['Bottom_words'] = word_count(bottomText)
		
		stat['Top_Paragraphs'] = paragraph_count(topText)
		stat['Left_Paragraphs'] = paragraph_count(leftText)
		stat['Bottom_Paragraphs'] = paragraph_count(bottomText)
		
		stat['Top_H1'] = h1_count(topText)
		stat['Left_H1'] = h1_count(leftText)
		stat['Bottom_H1'] = h1_count(bottomText)
		
		stat['Top_H2'] = h2_count(topText)
		stat['Left_H2'] = h2_count(leftText)
		stat['Bottom_H2'] = h2_count(bottomText)
		
		stat['Top_H3'] = h3_count(topText)
		stat['Left_H3'] = h3_count(leftText)
		stat['Bottom_H3'] = h3_count(bottomText)
		
		stat['Bottom_List'] = list_count(bottomText)
		stat['Bottom_Image'] = image_count(bottomText)
		stat['Bottom_Table'] = table_count(bottomText)
		stat['List_Broken'] = list_broken(bottomText)
		stat['Image_Borken'] = image_broken(bottomText)
		stat['Table_Borken'] = table_broken(bottomText)
		stat['Space_Borken'] = space_broken(bottomText)
		
		stats.append(stat)
		
	return stats
	
def read_data(filename):
	data = []
	with codecs.open(filename, 'r', 'utf-8') as data_file:
		for row in data_file:
			data.append(json.loads(row))
	return data

def output(stats):
	w = csv.DictWriter(sys.stdout,stats[0].keys())
	w.writerows(stats)

data = read_data(sys.argv[1])
stats = calculate_stats(data)
output(stats)
