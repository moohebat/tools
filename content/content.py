#!/usr/bin/python
# pip install lxml

import csv, codecs, json, re, sys
from collections import OrderedDict
from lxml import html, cssselect
from HTMLParser import HTMLParser

reload(sys)
sys.setdefaultencoding("UTF-8")	

# Simple Counts
def character_count(string):
	string = HTMLParser().unescape(re.sub('<[^<]+?>', '', string).strip())
	return len(string)
	
def word_count(string):
	string = HTMLParser().unescape(re.sub('<[^<]+?>', '', string).strip())
	matches = re.findall(r"[\w']+", string)
	return len(matches)
	
def paragraph_count(dom):
	elements = dom.cssselect("p")
	count = 0
	for e in elements:
		if not (e.text and e.text.strip() == ""):
			count = count + 1
	elements = dom.cssselect("br")
	for e in elements:
		count = count + 1
	return count

def h1_count(string):
	matches = re.findall(r"(</h1>)", string)
	return len(matches)
	
def h2_count(string):
	matches = re.findall(r"(</h2>)", string)
	return len(matches)

def h3_count(string):
	matches = re.findall(r"(</h3>)", string)
	return len(matches)

def list_count(string):
	matches = re.findall(r"(</ul>)|(</ol>)", string)
	return len(matches)

def table_count(string):
	matches = re.findall(r"(</table>)", string)
	return len(matches)

def image_count(string):
	matches = re.findall(r"(<img)", string)
	return len(matches)

def link_count(string):
	matches = re.findall(r"(</a>)", string)
	return len(matches)
	
def has_title(string):
	return len(string) > 0

def has_heading(string):
	return len(string) > 0

def has_meta(string):
	return len(string) > 0

def has_logo(string):
	return len(string) > 0

def int_url_count(array):
	count = 0
	for item in array:
		if len(item) > 0:
			count = count + 1
	return count
			
# HTML Rules
def single_item_list(dom):
	elements = dom.cssselect("ul, ol")
	broken = 0
	for e in elements:
		sub = e.cssselect("li")
		if len(sub) < 2:
			broken = broken + 1
	return broken
	
def empty_paragraph(dom):
	elements = dom.cssselect("p")
	broken = 0
	for e in elements:
		if e.text and e.text.strip() == "":
			broken = broken + 1
	return broken

def spaces_at_end(string):
	matches = re.findall(r"(&nbsp;</)|( </)", string)
	return len(matches)
	
def double_spaces(string):
	string = HTMLParser().unescape(re.sub('<[^<]+?>', '', string).strip())
	matches = re.findall(r"(&nbsp;&nbsp;)|(  )", string)
	return len(matches)
	
def missing_table_header(dom):
	elements = dom.cssselect("table")
	broken = 0
	for e in elements:
		sub = e.cssselect("th")
		if len(sub) == 0:
			broken = broken + 1
	return broken

def table_width_height(dom):
	elements = dom.cssselect("table, tr, th, td")
	broken = 0
	for e in elements:
		if (e.attrib and "style" in e.attrib) and ("width" in e.attrib['style'] or "height" in e.attrib['style']):
			broken = broken + 1
	return broken

def image_in_table(dom):
	tables = dom.cssselect("table")
	broken = 0
	for t in tables:
		images = t.cssselect("img")
		for i in images:
			broken = broken + 1
	return broken

def image_not_cdn(dom):
	elements = dom.cssselect("img")
	broken = 0
	for e in elements:
		if "iprice-prod" in e.attrib['src']:
			broken = broken + 1
	return broken

def get_field(field, row):
	if field in row['fields']:
		return str(row['fields'][field][0])
	else:
		return ''

def calculate_stats(data):
	stats = []
	for row in data:
		topText = get_field('shortText', row)
		leftText = get_field('sideText', row)
		bottomText = get_field('text', row)
		
		if not topText and not bottomText and not leftText:
			continue
		
		stat = OrderedDict()
		stat['URL'] = "/" + get_field('url', row) + "/"
		stat['CC'] = row['_index'].split("_")[1]
		
		type = row['_type']
		if type in ['brand', 'category', 'filtered']:
			stat['Product'] = 'Shop'
			if type == 'filtered':
				subProduct = [
					'brand' if get_field('source.brand', row) else '',
					'series' if get_field('source.series', row) else '',
					'model' if get_field('source.model', row) else '',
					'category' if get_field('source.category', row) else '',
					'gender' if get_field('source.gender', row) in ['1','2'] else '',
					'color' if get_field('source.color', row) else ''
				]
				stat['SubProduct'] = "-".join(filter(None, subProduct))
			else:
				stat['SubProduct'] = type
		elif type in ['blog', 'page']:
			stat['Product'] = 'Static'
			stat['SubProduct'] = type
		elif type in ['store', 'couponCategory']:
			stat['Product'] = 'Coupon'
			stat['SubProduct'] = type
			stat['URL'] = "/coupons" + stat['URL']
		else:
			print sys.stderr > "Unknown type: %s" % type
		
		domTopText = html.fragment_fromstring(topText, create_parent="div")
		domLeftText = html.fragment_fromstring(leftText, create_parent="div")
		domBottomText = html.fragment_fromstring(bottomText, create_parent="div")
		
		stat['Category_Overview'] = str(get_field('categoryOverview', row))
		stat['International_URLs'] = int_url_count([
			get_field('internationalUrl.HK', row),
			get_field('internationalUrl.ID', row),
			get_field('internationalUrl.MY', row),
			get_field('internationalUrl.PH', row),
			get_field('internationalUrl.SG', row),
			get_field('internationalUrl.TH', row),
			get_field('internationalUrl.VN', row)
		])
		
		stat['Has_Logo'] = str(has_logo(get_field('image', row)))
		stat['Has_Title'] = str(has_title(get_field('title', row)))
		stat['Has_Meta'] = str(has_meta(get_field('meta', row)))
		stat['Has_Heading'] = str(has_heading(get_field('heading', row)))
		
		stat['Top_Characters'] = character_count(topText)
		stat['Left_Character'] = character_count(leftText)
		stat['Bottom_Characters'] = character_count(bottomText)
		
		stat['Top_Words'] = word_count(topText)
		stat['Left_Words'] = word_count(leftText)
		stat['Bottom_Words'] = word_count(bottomText)
		
		stat['Top_Paragraphs'] = paragraph_count(domTopText)
		stat['Left_Paragraphs'] = paragraph_count(domLeftText)
		stat['Bottom_Paragraphs'] = paragraph_count(domBottomText)
		
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
		stat['Bottom_Links'] = link_count(bottomText)
		
		stat['Single_Item_List'] = single_item_list(domBottomText)
		stat['Empty_Paragraph'] = empty_paragraph(domBottomText)
		stat['Missing_Table_Header'] = missing_table_header(domBottomText)
		stat['Table_Width_Height'] = table_width_height(domBottomText)
		stat['Image_In_Table'] = image_in_table(domBottomText)
		stat['Image_Not_CDN'] = image_not_cdn(domBottomText)
		stat['Spaces_At_End'] = spaces_at_end(bottomText)
		stat['Double_Spaces'] = spaces_at_end(bottomText)
		
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
	w.writeheader()
	w.writerows(stats)

data = read_data(sys.argv[1])
stats = calculate_stats(data)
output(stats)
