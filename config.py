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
                c = json.load(f)
            self.width= int(c['general'].get('width', self.width))
            self.height= int(c['general'].get('height', self.height))
            self.background = c['general'].get('background', self.background)
            self.bg_fmt = c['general'].get('bg_fmt', self.bg_fmt)
            self.bg_color = c['general'].get('bg_color', self.bg_color)
            self.bg_src = c['general'].get('bg_src', self.bg_src)
            self.baseUrl = c['general'].get('baseUrl', self.baseUrl)
            self.albumIds = c['general'].get('albumIds', self.albumIds)
            self.contents = c['general'].get('contents', self.contents)
        except:
            pass

class Googleconfig:
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly', 'https://www.googleapis.com/auth/photoslibrary.readonly']
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
                c = json.load(f)
            self.calendarIds = c['calendar']['calendarIds']
            self.x = int(c['calendar'].get('x', self.x))
            self.y = int(c['calendar'].get('y', self.y))
            self.width = int(c['calendar'].get('width', self.width))
            self.height = int(c['calendar'].get('height', self.height))
            self.event_num = int(c['calendar'].get('event_num', self.event_num))
            self.font = c['calendar'].get('font', self.font)
            self.fontsize = int(c['calendar'].get('fontsize', self.fontsize))
            self.alpha = int(c['calendar'].get('alpha', self.alpha))
        except:
            print('No/Invalid config file')
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
                c = json.load(f)
            self.office = c['weather']['office']
            self.office_code = c['weather']['office_code']
            self.area = c['weather']['area']
            self.area_code = c['weather']['area_code']
            self.x = int(c['weather'].get('x', self.x))
            self.y = int(c['weather'].get('y', self.y))
            self.width= int(c['weather'].get('width', self.width))
            self.height= int(c['weather'].get('height', self.height))
            self.font = c['weather'].get('font', self.font)
            self.fontsize= int(c['weather'].get('fontsize', self.fontsize))
            self.icon_width= int(c['weather'].get('icon_width', self.icon_width))
            self.icon_height= int(c['weather'].get('icon_height', self.icon_height))
            self.alpha = int(c['weather'].get('alpha', self.alpha))

        except:
            print('No/Invalid config file')
            sys.exit()