import pandas, sys

def detect_zero_commission(order_value, commission):
    missing_order_value = False
    missing_commission = False
    
    if pandas.isnull(commission) or commission == 0:
        missing_commission = True
    if pandas.isnull(order_value) or order_value == 0:
        missing_order_value = True
    
    if missing_commission and missing_order_value:
        return "zero commission and order value"
    elif missing_commission:
        return "zero commission"
    elif missing_order_value:
        return "zero order value"

DUPLICATE_ORDERS = {}
def detect_duplicate_order(timestamp, order_id, order_value, commission):
    if pandas.isnull(commission) or pandas.isnull(order_value):
        return
        
    # the same basket was bought by the same person in 60 minutes (and rejected)
    id = str(int(timestamp/3600)) + str(commission) + str(order_value)
    if id in DUPLICATE_ORDERS:
        if not order_id in DUPLICATE_ORDERS[id]:
            DUPLICATE_ORDERS[id].append(order_id)
            # TODO (1): if status != 'approved':
            return "duplicate order"
    else:
        DUPLICATE_ORDERS[id] = [order_id]

def detect_abnormaly_high(order_value, status):
    # we never had an item/order >$2500 approved and only few with >$1000
    if status != 'approved' and order_value > 2500:
        return "abnormal order value"
    elif status != 'approved' and order_value > 1000:
        return "suspicious order value"

def detect(data):
    if not "ipg:suspicious" in data.columns.values:
        data['ipg:suspicious'] = pandas.np.nan
  
    data['ipg:suspicious'] = data.apply(lambda x: detect_zero_commission(x['ipg:orderValue'], x['ipg:commission']) \
     if pandas.isnull(x['ipg:suspicious']) else x['ipg:suspicious'], axis=1)
    
    data['ipg:suspicious'] = data.apply(lambda x: detect_abnormaly_high(x['ipg:orderValue'], x['ipg:status']) \
     if pandas.isnull(x['ipg:suspicious']) else x['ipg:suspicious'], axis=1)
    
    data = data.sort_values("ipg:status", ascending=True)
    data['ipg:suspicious'] = data.apply(lambda x: detect_duplicate_order(x['ipg:timestamp'], x['ipg:orderId'], x['ipg:orderValue'], x['ipg:commission']) \
     if pandas.isnull(x['ipg:suspicious']) else x['ipg:suspicious'], axis=1)
     
    return data
