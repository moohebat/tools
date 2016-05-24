#!/usr/bin/python
# TODO: Retry logic

import argparse, codecs, datetime, sys

from googleads import adwords
from progress.bar import Bar

reload(sys)
sys.setdefaultencoding("UTF-8")

countrycodes = {'MY':'2458','TH':'2764','ID':'2360','HK':'2344','SG':'2702','PH':'2608','VN':'2704'}

argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument('cc', type=str, help=('Country code).'))
argparser.add_argument('--stats', dest="stats", action='store_const', const=1, help=('Return keyword search volume).'))
argparser.add_argument('--ideas', dest="ideas", action='store_const', const=1, help=('Return keyword ideas).'))
argparser.add_argument('file', type=str, help=('File with one keyword per line).'))

PAGE_SIZE = 800

def query_adwords(service, cc, keywords, rtype):
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
      'requestType': rtype,
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
	service = client.GetService('TargetingIdeaService', version='v201601')
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
						cpc = int(attribute['value']['value']['microAmount']) / 1000000.0

			print '"%s"\t"%s"\t"%s"\t"%s"' % (keyword, sv, competition, cpc)

def read_file(filename):
	with codecs.open(filename, 'r', 'utf-8') as f:
		lines = [x.strip('\n') for x in f.readlines()]
	unique = set(lines)
	return list(unique)

def main(argv):
	args = argparser.parse_args()

	print >> sys.stderr, '# Start: Adwords Data: %s, %s' % (args.cc, datetime.datetime.now().time().isoformat())

	service = initialize_service()
	keywords = read_file(args.file)

	print '"%s"\t"%s"\t"%s"\t"%s"' % ("keyword", "sv (month)", "competition", "cpc ($)")

	bar = Bar('Processing', max=len(keywords), suffix ='%(percent).1f%% - %(eta)ds')
	if args.stats:
		# pagination of 800 items
		kws = keywords
		while len(kws) > 0:
			page = kws[0:PAGE_SIZE]
			kws = kws[PAGE_SIZE:]

			output(query_adwords(service, args.cc, page, "STATS"))

			bar.next(len(page))

	elif args.ideas:
		# pagination of 1 item
		for kw in keywords:
			output(get_keyword_suggestions(service, args.cc, "IDEAS"))

			bar.next()

	bar.finish()
	
	print >> sys.stderr, '# End: Adwords Data: %s, %s' % (args.cc, datetime.datetime.now().time().isoformat())

if __name__ == '__main__':
    main(sys.argv)
