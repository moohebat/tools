#!/usr/bin/python
# pip install lxml

import csv, codecs, datetime, json, re, sys
from collections import OrderedDict

reload(sys)
sys.setdefaultencoding("UTF-8")	

KNOWN_DOMAINS = [
	'click.linksynergy.com',
	'www.anrdoezrs.net',
	'www.dpbolvw.net',
	'www.jdoqocy.com',
	'www.kqzyfj.com',
	'www.tkqlhce.com',
	'list.qoo10.sg',
	'ho.lazada.co.id',
	'ho.lazada.co.th',
	'ho.lazada.com.my',
	'ho.lazada.com.ph',
	'ho.lazada.sg',
	'ho.lazada.vn',
	'zalorasea.go2cloud.org',
	'ipricegroup.go2cloud.org',
	'tracking.ipricegroup.com',
	'tr.styles.my',
	'tracking.shopstylers.com',
	'www.tagserve.asia',
	'www.tagserve.sg',
	'clk.omgt3.com',
	'track.omguk.com',
	'click.accesstrade.in.th',
	't.cfjump.com',
	'web1.sasa.com',
	'www.chinesean.com',
	'click.accesstrade.co.id',
	'click.accesstrade.vn',
	'mataharimall.go2cloud.org',
	'www.amazon.com',
	'lazada.go2cloud.org'
]

COUNTRY_DETECTION = {
	'ID' : [
		'WID=48450',
		'SID=1642',
		'aff_sub=ID',
		'7235442',
		'KHyMxhx7KKI',
		'accesstrade.co.id',
		'WID=56241'
	],
	'HK' : [
		'WID=50256',
		'SID=1645',
		'aff_sub=HK',
		'7234621',
		'E1yNmjjl8Ns',
		'WID=56245'
	],
	'MY' : [
		'WID=48197',
		'SID=1641',
		'aff_sub=MY',
		'7222670',
		'Y0u1ZUQdqsc',
		'WID=55621'
	],
	'PH' : [
		'WID=48322',
		'SID=1644',
		'aff_sub=PH',
		'7227631',
		'dShRodDYMH4',
		'WID=56243'
	],
	'SG' : [
		'WID=48321',
		'SID=1637',
		'aff_sub=SG',
		'7227624',
		'mELKDSg1Hh8',
		'WID=56240'
	],
	'TH' : [
		'WID=57201',
		'SID=1638',
		'aff_sub=TH',
		'7306110',
		'BsXpHN2foVU',
		'accesstrade.in.th',
		'WID=56244'
	],
	'VN' : [
		'WID=48593',
		'SID=1643',
		'aff_sub=VN',
		'7236511',
		'lbvZkl*f46A',
		'accesstrade.vn',
		'WID=56242'
	]
	
}

def is_active(timestamp):
	seconds = int(timestamp) / 1000
	expires = datetime.datetime.fromtimestamp(seconds)
	now = datetime.datetime.now()
	if now < expires:
		return True
	else:
		return False

def unknown_tracking(urls):
	unknown = True
	for domain in KNOWN_DOMAINS:
		for url in urls:
			if domain in url:
				unknown = False
				break
	return unknown
	
def detect_country(url):
	country = ""
	for cc, schemas in COUNTRY_DETECTION.iteritems():
		for schema in schemas:
			schema = schema.lower()
			if schema in url:
				country = cc	
				break
	return country

def get_field(field, row):
	if field in row['fields']:
		return str(row['fields'][field][0])
	else:
		return ''

def calculate_stats(data):
	stats = []
	for row in data:
	
		stat = OrderedDict()
	
		expires = get_field('expires', row)
		referral = get_field('referral', row).lower()
		referralMobile = get_field('referralMobile', row).lower()
		store = get_field('store.url', row)
		category = get_field('category.url', row)
		popularity = get_field('popularity', row)
		
		stat['Store'] = store
		stat['Category'] = category
		stat['Popularity'] = popularity
		stat['Active'] = is_active(expires)
		stat['Unknown_Tracking'] = unknown_tracking([referral, referralMobile])
		stat['Tracking_CC'] = detect_country(referral)
		stat['Tracking_CC_Mobile'] = detect_country(referralMobile)
		stat['Referral'] = referral
		stat['ReferralMobile'] = referralMobile
		
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
