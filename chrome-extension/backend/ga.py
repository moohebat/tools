# DEPENDENCIES
# $ sudo pip install requests
# $ sudo pip install python-firebase
# $ sudo pip install google-api-python-client

from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

from datetime import datetime, timedelta
from pytz import timezone
from firebase import firebase

import calendar, httplib2, json

service_account_email = 'chrome-extension@molten-nirvana-810.iam.gserviceaccount.com'
key_file_location = 'ga.p12'
scope = 'https://www.googleapis.com/auth/analytics.readonly'
discovery = 'https://analyticsreporting.googleapis.com/$discovery/rest'

GOAL = 1338666 # one million

FIREBASE = 'https://vivid-inferno-7935.firebaseIO.com'

PROFILES = dict()
PROFILES['SG'] = '75448761'
PROFILES['MY'] = '75229758'
PROFILES['ID'] = '75897118'
PROFILES['PH'] = '75445974'
PROFILES['TH'] = '79109064'
PROFILES['VN'] = '75895336'
PROFILES['HK'] = '75887160'

def get_sessions(service):
  year = datetime.now(timezone('Asia/Kuala_Lumpur')).year
  month = datetime.now(timezone('Asia/Kuala_Lumpur')).month
  day = datetime.now(timezone('Asia/Kuala_Lumpur')).day
  hour = datetime.now(timezone('Asia/Kuala_Lumpur')).hour
  minute = datetime.now(timezone('Asia/Kuala_Lumpur')).minute
  weekday = datetime.now(timezone('Asia/Kuala_Lumpur')).weekday()

  start_current_month = datetime(year, month, 1)
  if day == 1:
    end_current_month = start_current_month
  else:
    end_current_month = datetime(year, month, day) - timedelta(days=1)

  if weekday == 0:
    weekday = 7
  start_current_week = datetime(year, month, day) - timedelta(days=weekday)
  end_current_week = datetime(year, month, day) - timedelta(days=1)

  start_last_month = datetime(year, month - 1, 1)
  last_day_month = calendar.monthrange(year, month - 1)[1]
  if day > last_day_month:
    end_last_month = datetime(year, month - 1, last_day_month)
  else:
    end_last_month = datetime(year, month - 1, day) - timedelta(days=1)

  start_last_week = start_current_week - timedelta(days=7)
  end_last_week = end_current_week - timedelta(days=7)

  total, none = query_ga(service, start_current_month, datetime.now(timezone('Asia/Kuala_Lumpur')), start_current_month, datetime.now(timezone('Asia/Kuala_Lumpur')))
  this_month, last_month = query_ga(service, start_current_month, end_current_month, start_last_month, end_last_month)
  this_week, last_week = query_ga(service, start_current_week, end_current_week, start_last_week, end_last_week)

  return (total, this_month, last_month, this_week, last_week)

def query_ga(service, firstStartDate, firstEndDate, secondStartDate, secondEndDate):
  first, second = 0, 0

  for cc, profile in PROFILES.iteritems():

    data = service.reports().batchGet(
    body={
      "reportRequests": {
        "viewId": 'ga:' + profile,
        "dateRanges":[
          {
            "startDate": firstStartDate.strftime("%Y-%m-%d"),
            "endDate": firstEndDate.strftime("%Y-%m-%d")
          },
          {
            "startDate": secondStartDate.strftime("%Y-%m-%d"),
            "endDate": secondEndDate.strftime("%Y-%m-%d")
          }
        ],
        "metrics":[
          {
            "expression":"ga:sessions"
          }]
        }
    }
    ).execute()

    first = first + int(data['reports'][0]['data']['rows'][0]['metrics'][0]['values'][0])
    second = second + int(data['reports'][0]['data']['rows'][0]['metrics'][1]['values'][0])

  return first, second

def create_service():
	credentials = ServiceAccountCredentials.from_p12_keyfile(service_account_email, key_file_location, scopes=[scope])
	http = credentials.authorize(httplib2.Http())
	return build("analyticsreporting", "v4", http=http, discoveryServiceUrl=discovery)

def get_increment(sessions):
	now = datetime.now(timezone('Asia/Kuala_Lumpur'))
	seconds = ((now.day - 1) * 24 * 60 * 60) + (now.hour * 60 * 60) + (now.minute * 60) + now.second
	return sessions / float(seconds)

def get_goal_date(per_second, sessions):
	remaining = GOAL - sessions
	seconds = remaining / per_second
	timestamp = datetime.now(timezone('Asia/Kuala_Lumpur')) + timedelta(seconds=seconds)
	return (timestamp.strftime("%d.%m.%Y"), timestamp.strftime("%H:%M"))

def write_data(values):
	fb = firebase.FirebaseApplication(FIREBASE, None)
	fb.put("/metrics", "ga", values)

service = create_service()
sessions = get_sessions(service)
increment = get_increment(sessions[0])
goal_date = get_goal_date(increment, sessions[0])
mom = '{:.1%}'.format((sessions[1] / float(sessions[2])) - 1)
wow = '{:.1%}'.format((sessions[3] / float(sessions[4])) - 1)

write_data([sessions[0], increment, GOAL, goal_date[0], goal_date[1], mom, wow])

