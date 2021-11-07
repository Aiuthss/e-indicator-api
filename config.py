from __future__ import print_function
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import json
import sys

class Config:
    def __init__(self, config_file):
        self.general = Generalconfig(config_file)
        self.google = Googleconfig()
        for i in self.general.contents:
            if i == 'calendar':
                self.calendar = Calendarconfig(config_file)
            elif i == 'weather':
                self.weather = Weatherconfig(config_file)
            elif i == 'tasks':
                self.tasks = Tasksconfig(config_file)

class Generalconfig:
    width = 600
    height = 448
    background = None
    bg_fmt = 'full'
    bg_color = 'white'
    bg_src = None
    albumIds = []
    baseUrl = None
    contents = ['weather', 'calendar']

    def __init__(self, config_file):
        try:
            with open(config_file, 'r', encoding='UTF-8') as f:
                w = json.load(f)
            self.width= int(w['general'].get('width', self.width))
            self.height= int(w['general'].get('height', self.height))
            self.background = w['general'].get('background', self.background)
            self.bg_fmt = w['general'].get('bg_fmt', self.bg_fmt)
            self.bg_color = w['general'].get('bg_color', self.bg_color)
            self.bg_src = w['general'].get('bg_src', self.bg_src)
            self.baseUrl = w['general'].get('baseUrl', self.baseUrl)
            self.albumIds = w['general'].get('albumIds', self.albumIds)
            self.contents = w['general'].get('contents', self.contents)
        except:
            pass

class Googleconfig:
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly', 'https://www.googleapis.com/auth/photoslibrary.readonly', 'https://www.googleapis.com/auth/tasks.readonly']
    def __init__(self):
        self.creds = None
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', self.SCOPES)
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())

class Calendarconfig:
    calendarIds = []
    x = 200
    y = 0
    width = 400
    height = 448
    event_num = 4
    font = 'NotoSansJP-Black.otf'
    fontsize = 8
    alpha = 150

    def __init__(self, config_file):
        try:
            with open(config_file, 'r', encoding='UTF-8') as f:
                w = json.load(f)
            self.calendarIds = w['calendar']['calendarIds']
            self.x = int(w['calendar'].get('x', self.x))
            self.y = int(w['calendar'].get('y', self.y))
            self.width = int(w['calendar'].get('width', self.width))
            self.height = int(w['calendar'].get('height', self.height))
            self.event_num = int(w['calendar'].get('event_num', self.event_num))
            self.font = 'fonts/' + w['calendar'].get('font', self.font)
            self.fontsize = int(w['calendar'].get('fontsize', self.fontsize))
            self.alpha = int(w['calendar'].get('alpha', self.alpha))
        except:
            print('No/Invalid calendar config')
            sys.exit()

class Weatherconfig:
    office = None
    office_code = None
    area = None
    area_code = None
    x = 0
    y = 0
    width = 200
    height = 150
    font = 'NotoSansJP-Black.otf'
    fontsize = 13
    icon_width = 80
    icon_height = 60
    alpha = 150

    def __init__(self,config_file):
        try:
            with open(config_file, 'r', encoding='UTF-8') as f:
                w = json.load(f)
            weather = w['weather']
            self.office = weather['office']
            self.office_code = weather['office_code']
            self.area = weather['area']
            self.area_code = weather['area_code']
            self.x = int(weather.get('x', self.x))
            self.y = int(weather.get('y', self.y))
            self.width= int(weather.get('width', self.width))
            self.height= int(weather.get('height', self.height))
            self.font = 'fonts/' + weather.get('font', self.font)
            self.fontsize= int(weather.get('fontsize', self.fontsize))
            self.icon_width= int(weather.get('icon_width', self.icon_width))
            self.icon_height= int(weather.get('icon_height', self.icon_height))
            self.alpha = int(weather.get('alpha', self.alpha))

        except:
            print('No/Invalid weather config')
            sys.exit()

class Tasksconfig:
    tasklistIds = []
    x = 0
    y = 150
    width = 200
    height = 298
    max_tasks = 5
    font = 'NotoSansJP-Black.otf'
    fontsize = 15
    alpha = 150

    def __init__(self, config_file):
        try:
            with open(config_file, 'r', encoding='UTF-8') as f:
                t = json.load(f)
            tasks = t['tasks']
            self.tasklistIds = tasks['tasklistIds']
            self.x = int(tasks.get('x', self.x))
            self.y = int(tasks.get('y', self.y))
            self.width = int(tasks.get('width', self.width))
            self.height = int(tasks.get('height', self.height))
            self.max_tasks = int(tasks.get('max_tasks', self.max_tasks))
            self.font = 'fonts/' + tasks.get('font', self.font)
            self.fontsize = int(tasks.get('fontsize', self.fontsize))
            self.alpha = int(tasks.get('alpha', self.alpha))
        except:
            print('No/Invalid task config')
            sys.exit()