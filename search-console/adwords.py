#!/usr/bin/python
# TODO: Retry logic

import argparse, codecs, sys

from googleads import adwords

reload(sys)
sys.setdefaultencoding("UTF-8")

countrycodes={'MY':'2458','TH':'2764','ID':'2360','HK':'2344','SG':'2702','PH':'2608','VN':'2704'}

argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument('cc', type=str, help=('Country code).'))
argparser.add_argument('--stats', dest="stats", action='store_const', const=1, help=('Return keyword search volume).'))
argparser.add_argument('--ideas', dest="ideas", action='store_const', const=1, help=('Return keyword ideas).'))
argparser.add_argument('file', type=str, help=('File with one keyword per line).'))

PAGE_SIZE = 800

def get_search_volume(service, cc, keywords):
	selector = {
      'searchParameters': [
          {
            'xsi_type': 'RelatedToQuerySearchParameter',
            'queries': [keywords]
          },
          {
            'xsi_type': 'LocationSearchParameter',
            'locations': [{'id':countrycodes[cc]}]
          }
      ],
      'ideaType': 'KEYWORD',
      'requestType': 'STATS',
      'requestedAttributeTypes': ['KEYWORD_TEXT', 'SEARCH_VOLUME','COMPETITION','AVERAGE_CPC'], #,'CATEGORY_PRODUCTS_AND_SERVICES'
      'paging': {
          'startIndex': str(0),
          'numberResults': str(PAGE_SIZE)
      },
      'currencyCode': 'USD'
    }

	return service.get(selector)

def get_keyword_suggestions(service, cc, keywords):
	selector = {
      'searchParameters': [
          {
            'xsi_type': 'RelatedToQuerySearchParameter',
            'queries': [keywords]
          },
          {
            'xsi_type': 'LocationSearchParameter',
            'locations': [{'id':countrycodes[cc]}]
          }
      ],
      'ideaType': 'KEYWORD',
      'requestType': 'IDEAS',
      'requestedAttributeTypes': ['KEYWORD_TEXT', 'SEARCH_VOLUME','COMPETITION','AVERAGE_CPC'], #,'CATEGORY_PRODUCTS_AND_SERVICES'
      'paging': {
          'startIndex': str(0),
          'numberResults': str(PAGE_SIZE)
      },
      'currencyCode': 'USD'
    }
	
	return service.get(selector)

def initialize_service():
	client = adwords.AdWordsClient.LoadFromStorage('googleads.yaml')
	service = client.GetService('TargetingIdeaService', version='v201506')
	return service

def output(data):
	if 'entries' in data:
		for result in data['entries']:
			keyword, sv, competition, cpc = "", "", "", ""
			for attribute in result['data']:
				if attribute['key'] == 'KEYWORD_TEXT':
					if 'value' in attribute['value']:
						keyword = attribute['value']['value']
				elif attribute['key'] == 'SEARCH_VOLUME':
					if 'value' in attribute['value']:
						sv = attribute['value']['value']
				elif attribute['key'] == 'COMPETITION':
					if 'value' in attribute['value']:
						competition = attribute['value']['value']
				elif attribute['key'] == 'AVERAGE_CPC':
					if 'value' in attribute['value']:
						cpc = attribute['value']['value']['microAmount']

			print '"%s"\t"%s"\t"%s"\t"%s"' % (keyword, sv, competition, cpc)

def read_file(filename):
	with codecs.open(filename, 'r', 'utf-8') as f:
		lines = [x.strip('\n') for x in f.readlines()]
	unique = set(lines)
	return list(unique)

def main(argv):
	args = argparser.parse_args()

	service = initialize_service()
	keywords = read_file(args.file)

	print keywords[0]

	if args.stats:
		# pagination of 800 items
		kws = keywords
		while len(kws) > 0:
			page = kws[0:800]
			kws = kws[800:]

			data = get_search_volume(service, args.cc, page)
			output(data)

	if args.ideas:
		# pagination of 1 item
		for kw in keywords:
			print kw
			data = get_keyword_suggestions(service, args.cc, kw)
			output(data)
    
if __name__ == '__main__':
    main(sys.argv)
