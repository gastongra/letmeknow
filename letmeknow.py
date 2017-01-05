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
from kivy.uix.textinput import TextInput
from kivy.garden import circulardatetimepicker

import datetime
import time

from kivy.uix.label import Label
###################################################
### imports para google calendar 
import httplib2
import os
from oauth2client import tools
from oauth2client.file import Storage
from apiclient import discovery
from oauth2client import client
###################################################

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'AgendaApp'


Builder.load_file('letmeknow.kv')

########################################################################
'''
Class Calendario needed to overwrite on_touch_up method from parent class CalendarWidget.
This is to avoid bubling of the event, 
as explained in https://kivy.org/docs/api-kivy.uix.widget.html#widget-event-bubbling:

	In order to stop this event bubbling, a method can return True. 
	This tells Kivy the event has been handled and the event propagation stops. 
	For example:

	class MyWidget(Widget):
		def on_touch_down(self, touch):
			If <some_condition>:
				# Do stuff here and kill the event
				return True
			else:
				return super(MyWidget, self).on_touch_down(touch)

'''
class Calendario(CalendarWidget):
	def on_touch_up(self, touch):
		return True


class Home(Screen):
	pass

class Startup(Screen):
	pass

class Evento(Screen):
	pass
					
class SaveDismiss(Widget):
	pass


						
class LetMeKnowApp(App):

	def build(self):
		sm = ScreenManager()

#		startup = Screen(name='startup')
#		startup.add_widget(Label(text='Loading ...'))
		startup=Startup(name='startup')
		sm.add_widget(startup)

		#home.myLabel.text = "hola!!"
		#home.myLabel.bind(text=home.myButton.setter('text'))
		
		home = Home(name='home')
		sm.add_widget(home)
		
		evento = Evento(name='evento')
		sm.add_widget(evento)


#		sm.current = 'home'

		return sm


	def get_credentials(self):
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



	def get_events(self):
		
		print('antes: ',self.root.get_screen('startup').myLabel.text)
		self.root.get_screen('startup').myLabel.text = 'Loading your Calendar. Please wait ...'
		print('despues: ',self.root.get_screen('startup').myLabel.text)
		credentials = self.get_credentials()
		http = credentials.authorize(httplib2.Http())

		print('********************',datetime.datetime.now())
		print('Getting upcoming events. This might take a while ...')
		service = discovery.build('calendar', 'v3', http=http)
		print('********************',datetime.datetime.now())

		now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
		eventsResult = service.events().list(
		calendarId='primary', timeMin=now, maxResults=100, singleEvents=True,
		orderBy='startTime').execute()
		self.events = eventsResult.get('items', [])
		
		self.root.current = 'home'


	def showEvents(self):
		#Busca las citas del calendario correspondientes al dia seleccionado
		#y las muestra en el label de la home screen
		dia, mes, anio = self.root.get_screen('home').myCalendar.active_date
		dt_fecha_actual = datetime.datetime(day=dia, month=mes, year=anio)
		str_fecha_actual = dt_fecha_actual.strftime("%d-%m-%Y")

		if not self.events:
		#if not root.get_screen('home').myCalendar.
			
			
			print('No upcoming events found.')

		str_eventos = ''
		for event in self.events:
			str_summary = str(event['summary'] )
			str_inicio = str(event['start'].get('dateTime'))[0:19] #2016-12-20T11:30:00-03:00
			dt_inicio = datetime.datetime.strptime(str_inicio, "%Y-%m-%dT%H:%M:%S")

			#getting date and time:
			str_fecha_ev = dt_inicio.strftime("%d-%m-%Y")
			str_hora_ev = dt_inicio.strftime("%H:%M")
			if str_fecha_actual == str_fecha_ev:
				str_detalle_ev = str_fecha_ev + ' - ' + str_hora_ev + ' - ' + str_summary
				print(str_detalle_ev)
				str_eventos += str_detalle_ev + '\n'
			
		self.root.get_screen('home').myLabel.text = str_eventos

	def createEvent(self, ev_date):
		#dia, mes, anio = self.root.get_screen('home').myCalendar.active_date
		dia, mes, anio = ev_date
		#dt_fecha_actual = datetime.datetime(day=dia, month=mes, year=anio)
		#str_fecha_actual = dt_fecha_actual.strftime("%d-%m-%Y")
		self.root.current = 'evento'
	
		
		
if __name__ == '__main__':
    LetMeKnowApp().run()

	
