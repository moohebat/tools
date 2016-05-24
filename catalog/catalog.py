#!/usr/bin/python
# pip install elasticsearch
# pip install elasticsearch-dsl

import argparse, datetime, urllib, socket, sys, pandas, elasticsearch, urllib3, time

reload(sys)
sys.setdefaultencoding("UTF-8")
socket.setdefaulttimeout(10)
urllib3.disable_warnings()


argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument('cc', type=str, help=('Country code).'))

DB = 'https://search-iprice-production-7-pluvqb7oq6wnsisr4k6j62qtlq.ap-southeast-1.es.amazonaws.com'
QUERY = {
    "aggs" : {
        "stores" : {
            "terms" : {
                "field": "store.url",
                "size" : 0
            },
            "aggs" : {
                "urls" : {
                    "terms" : {
                        "field" : "XXX.url",
                        "size" : 0
                    },
                    "aggs" : {
                      "details" : {
                          "top_hits" : {
                              "_source" : {
                                  "include" :[
                                      "brand.url",
                                      "series.url"
                                  ]
                              },
                              "size" : 1
                          }
                      }
                    }
                },
                "details" : {
                    "top_hits" : {
                        "_source" : {
                            "include" :[
                                "store.merchant_id",
                                "store.country",
                                "store.shipping"
                            ]
                        },
                        "size" : 1
                    }
                }
            }
        }
    }
}

def get_data(cc, query, thing):
  retry = 3
  while retry:
    es = elasticsearch.Elasticsearch(DB)
    query = QUERY.copy()
    query["aggs"]["stores"]["aggs"]["urls"]["terms"]["field"] = thing
    
    try:
      res = es.search(index="product_" + cc.lower(), body=query, search_type="count")
      return res['aggregations']
    except elasticsearch.exceptions.AuthorizationException:
      retry = retry -1
    except elasticsearch.exceptions.ConnectionTimeout:
      retry = retry -1
      time.sleep(10)
  
  print >> sys.stderr, "ERROR: Couldn't download data for %s" % (thing)
  return None

def output(cc, data):
  
  headers = ['CC', 'MerchantName', 'MerchantID', 'MerchantCountry', 'MerchantShipping', 'URL', 'Type', 'Products']
  
  array = []
  for thing, aggs in data.iteritems():
    if aggs:
      for store in aggs['stores']['buckets']:
        for url in store['urls']['buckets']:
          # skip emtpy buckets
          if str(url['key']) == "0" or str(url['key']) == "":
            continue
        
          item = []
          item += [cc]
          item += [store['key']]
          item += [store['details']['hits']['hits'][0]['_source']['store']['merchant_id']]
          item += [store['details']['hits']['hits'][0]['_source']['store']['country']]
          item += [store['details']['hits']['hits'][0]['_source']['store']['shipping']]

          if thing == 'gender':
            if url['key'] == 1:
              item += ["men"]
            elif url['key'] == 2:
              item += ['women']
            else:
              item += ["/" + str(url['key'])]
              
          elif thing == 'model':
            brand = url['details']['hits']['hits'][0]['_source']['brand']['url']
            series = url['details']['hits']['hits'][0]['_source']['series']['url']
            model = str(url['key'])
            item += ['/' + '/'.join([brand, series, model])]
            
          elif thing == 'series':
            brand = url['details']['hits']['hits'][0]['_source']['brand']['url']
            series = str(url['key'])
            item += ['/' + '/'.join([brand, series])]
            
          else:
            item += ["/" + str(url['key'])]
            
          item += [thing]
          item += [url['doc_count']]
          
          array += [item]
  
  # totals
  for thing, aggs in data.iteritems():
    if aggs:
      for store in aggs['stores']['buckets']:
        item = []
        item += [cc]
        item += [store['key']]
        item += [store['details']['hits']['hits'][0]['_source']['store']['merchant_id']]
        item += [store['details']['hits']['hits'][0]['_source']['store']['country']]
        item += [store['details']['hits']['hits'][0]['_source']['store']['shipping']]
        item += ["/"]
        item += ["totals"]
        item += [store['doc_count']]
        array += [item]
    break
    
  output = pandas.DataFrame(array, columns=headers)
  output.to_csv(sys.stdout, header=True, index=False)


def main(argv):
  args = argparser.parse_args()

  print >> sys.stderr, '# Start: Catalog Data: %s, %s' % (args.cc, datetime.datetime.now().time().isoformat())

  data = dict()
  data['category'] = get_data(args.cc, QUERY, "category.url")
  data['brand'] = get_data(args.cc, QUERY, "brand.url")
  data['model'] = get_data(args.cc, QUERY, "model.url")
  data['series'] = get_data(args.cc, QUERY, "series.url")
  data['color'] = get_data(args.cc, QUERY, "color")
  data['gender'] = get_data(args.cc, QUERY, "gender")
  
  output(args.cc, data)
  
  print >> sys.stderr, '# End: Catalog Data: %s, %s' % (args.cc, datetime.datetime.now().time().isoformat())

if __name__ == '__main__':
    main(sys.argv)
