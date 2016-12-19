#! usr/bin/python
# -*- coding: utf-8 -*-
########################################################################
# Let Me Know - Organizador de Agenda
# Integra Google Calendar con Whatsapp
# Permite crear un evento del calendar de google y enviar un aviso por whatsapp
########################################################################

###################################################

from kivy.app import App
from kivy.uix.widget import Widget
from KivyCalendar import CalendarWidget
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
import datetime

###################################################
### imports para google calendar 
import httplib2
import os
from oauth2client import tools
from oauth2client.file import Storage
from apiclient import discovery

###################################################

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'secret_key.json'
APPLICATION_NAME = 'LetMeKnowApp'


Builder.load_file('letmeknow.kv')



def get_credentials():
#Gets valid user credentials from storage.
#If nothing has been stored, or if the stored credentials are invalid,
#the OAuth2 flow is completed to obtain the new credentials.

	home_dir = os.path.expanduser('~')
	credential_dir = os.path.join(home_dir, '.credentials')
	if not os.path.exists(credential_dir):
		os.makedirs(credential_dir)
	credential_path = os.path.join(credential_dir,
		   'calendar-python-quickstart.json')

	store = Storage(credential_path)
	credentials = store.get()
	if not credentials or credentials.invalid:
		flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
		flow.user_agent = APPLICATION_NAME
		if flags:
			credentials = tools.run_flow(flow, store, flags)
		else: # Needed only for compatibility with Python 2.6
			credentials = tools.run(flow, store)
		print('Storing credentials to ' + credential_path)
	return credentials

class Home(Screen):

	def showEvents(self):
		#Busca las citas del calendario correspondientes al dia seleccionado
		#y las muestra en el label de la home screen
		
		#self.eventos_fecha = self.myCalendar.text
		fecha = self.myCalendar.active_date
		print(fecha)
		self.myLabel.text = "%s.%s.%s" % tuple(self.myCalendar.active_date)
		print("Label: " + self.myLabel.text)
		
		credentials = get_credentials()
		http = credentials.authorize(httplib2.Http())
		service = discovery.build('calendar', 'v3', http=http)

		now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
		print('Getting upcoming events. This might take a while ...')
		eventsResult = service.events().list(
		calendarId='primary', timeMin=now, maxResults=100, singleEvents=True,
		orderBy='startTime').execute()
		events = eventsResult.get('items', [])
		
		
		
		#self.eventos_fecha = self.myCalendar.text
		#self.datepicked = datetime.datetime.strptime(self.laDate, '%d.%m.%Y').strftime('%d/%m/%Y')
		#self.myLabel.text = str(self.datepicked)
		#self.myLabel.text = "%s.%s.%s" % tuple(self.myCalendar.active_date)
		eventosDeHoy = ''
		if not events:
			print('No upcoming events found.')
		for event in events:
			inicio = str(event['start'].get('date'))
			summary = str(event['summary'] )
			print(inicio, summary)
			eventosDeHoy += inicio + ' - ' + summary + '\n'
		self.myLabel.text = eventosDeHoy

class LetMeKnowApp(App):

	def build(self):
		sm = ScreenManager()
		sm.add_widget(Home(name='home'))

		return sm

if __name__ == '__main__':
    LetMeKnowApp().run()

	
