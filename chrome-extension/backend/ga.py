
# REQUIREMENTS
# $ sudo pip install requests
# $ sudo pip install python-firebase
# $ sudo pip 
# $ sudo pip install google-api-python-client

from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

from datetime import datetime, timedelta
from firebase import firebase

import httplib2, json

service_account_email = 'chrome-extension@molten-nirvana-810.iam.gserviceaccount.com'
key_file_location = 'ga.p12'
scope = 'https://www.googleapis.com/auth/analytics.readonly'

GOAL = 1100000 # one million

FIREBASE = 'https://vivid-inferno-7935.firebaseIO.com'

PROFILES = dict()
PROFILES['SG'] = '75448761'
PROFILES['MY'] = '75229758'
PROFILES['ID'] = '75897118'
PROFILES['PH'] = '75445974'
PROFILES['TH'] = '79109064'
PROFILES['VN'] = '75895336'
PROFILES['HK'] = '75887160'

def query_sessions(service, profile_id):
  start_date = datetime.now().strftime("%Y-%m") + "-01"
  data = service.data().ga().get(
      ids='ga:' + profile_id,
      start_date=start_date,
      end_date='today',
      metrics='ga:sessions').execute()
  return int(data['rows'][0][0])

def create_service():
	credentials = ServiceAccountCredentials.from_p12_keyfile(service_account_email, key_file_location, scopes=[scope])
	http = credentials.authorize(httplib2.Http())
	return build("analytics", "v3", http=http)

def get_total_sessions(service):
	sessions = 0
	for cc, profile in PROFILES.iteritems():
		sessions = sessions + query_sessions(service, profile)
	return sessions

def get_increment(sessions):
	now = datetime.now()
	seconds = ((now.day - 1) * 24 * 60 * 60) + (now.hour * 60 * 60) + (now.minute * 60) + now.second
	return sessions / float(seconds)

def get_goal_date(per_second):
	remaining = GOAL - sessions
	seconds = remaining / per_second
	timestamp = datetime.now() + timedelta(seconds=seconds)
	return (timestamp.strftime("%d.%m.%Y"), timestamp.strftime("%H:%M"))

def write_data(values):
	fb = firebase.FirebaseApplication(FIREBASE, None)
	fb.put("/metrics", "ga", values)

service = create_service()
sessions = get_total_sessions(service)
increment = get_increment(sessions)
goal_date = get_goal_date(increment)

write_data([sessions, increment, GOAL, goal_date[0], goal_date[1]])

