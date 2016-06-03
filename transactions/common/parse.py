import datetime, md5, pandas, re, sys

def parse_datetime(value, format = "%Y-%m-%d %H:%M:%S"):
    dt = datetime.datetime.strptime(value, format)
    return (dt - datetime.datetime(1970, 1, 1)).total_seconds()

def detect_datetime(timestamp):
    dt = datetime.datetime.fromtimestamp(timestamp)
    return (dt.date().isoformat(),
        str(dt.year) + "-" + str(dt.strftime("%m")),
        str(dt.year) + "-" + str(dt.isocalendar()[1]),
        dt.time().isoformat())

PARTNERS = {
    'MP1000': 'SAYS',
    'MP0001': 'SAYS', # backwards compatibility
    'MP1001': 'JUICE',
    'MP1002': 'HANGER',
    'MP1003': 'RAPPLER',
    'MP1004': 'OHBULAN'
}

def detect_site(source):
  # TODO (-1): take aff_sub fields into account
  if pandas.notnull(source):
    matches = re.search("(MP[0-9]{4})", source)
    if matches:
        if matches.groups(0)[0] in PARTNERS:
            return PARTNERS[matches.groups(0)[0]]
        else:
            print >> sys.stderr, "Invalid partner ID detected: %s" % matches.groups(0)[0] 
        
  return "IPRICE"
  
def detect_channel(source):
    # TODO (-1): take aff_sub fields into account
    if pandas.notnull(source):
        matches = re.search("(organic|adwords|newsletter|news|referral|direct|social)", source)
        if matches:
            value = matches.groups(0)[0]
            if value == "newsletter":
                value = "news"
            return value
        
    return pandas.np.nan

def detect_product(source, sessionId):
    # TODO (-1): we could add offer name here for improving historic accuracy
    # TODO (-1): take aff_sub fields into account
 
    if pandas.notnull(source):
        # media partners are always coupon 
        matches = re.search("(MP[0-9]{4})", source)
        if matches:
            return "coupon"
    
        if source == "newsletter":
            return "news"
            
        # else check against possible values
        matches = re.search("(shop|coupon|blog)", source)
        if matches:
            return matches.group(0)
            
        # initially we only specific source if it was coupons
        if sessionId:
            return "shop"
            
    return pandas.np.nan
    
def detect_tracking_id(source):
    if pandas.notnull(source):
        # special case a bug in the generation of source fields
        source = source.replace("self-redirect-301", "redirect")
    
        fields = source.split("-", 2)
        if len(fields) == 3:
            id = fields[2]
            if len(id) == 11 or len(id) == 10 or len(id) == 9 or len(id) == 20:
                return id
        
    return pandas.np.nan

# TODO (0): Fill out complete table
MERCHANTS = {
    'Amnig': 'Amnig|ST148'
}
def detect_merchant(value):
    if value in MERCHANTS:
        return MERCHANTS[value].split("|")
    else:
        print >> sys.stderr, "Couldn't detect merchant ID for: %s" % value
        
    return (value, pandas.np.nan)


def detect_orderid(timestamp, session_id):
    # otherwise, ordersare made with the same sessionId within 10 seconds are considered one basket
    timestamp = int(timestamp/10)
    return "ipg/" + md5.new(str(timestamp) + str(session_id)).hexdigest()
