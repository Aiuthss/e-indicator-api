from __future__ import print_function
import os
from googleapiclient.discovery import build
import datetime
from PIL import Image, ImageDraw, ImageFont
import calendar_variance
import calendar

class Calendar:
    today = None
    timeMin = None
    timeMax = None
    days = None
    service = None
    events_info = None

    def __init__(self):
        self.today = datetime.datetime.now()
        self.days = calendar.Calendar().monthdatescalendar(self.today.year, self.today.month)
        self.timeMin = self.days[0][0].strftime('%Y-%m-%dT00:00:00+09:00')
        self.timeMax = (self.days[-1][-1] + datetime.timedelta(days=1)).strftime('%Y-%m-%dT00:00:00+09:00')

    def OAuth2(self, creds):
        self.service = build('calendar', 'v3', credentials=creds)

    def collect_events_info(self, config):
        self.events_info = []
        for calendarId in config.calendarIds:
            eventList = self.service.events().list(calendarId=calendarId, timeMax=self.timeMax, timeMin=self.timeMin, singleEvents=True, orderBy='startTime').execute()
            n_events = len(eventList["items"])
            events_info = []
            for i in range(0, n_events):
                event = eventList["items"][i]
                start = event.get('start', None)
                end = event.get('end', None)
                if 'date' in start:
                    start = datetime.datetime.strptime(start['date'], '%Y-%m-%d')
                    start = datetime.date(start.year, start.month, start.day)
                    end = datetime.datetime.strptime(end['date'], '%Y-%m-%d') - datetime.timedelta(days=1)
                    end = datetime.date(end.year, end.month, end.day)
                elif 'dateTime' in start:
                    start = datetime.datetime.strptime(start['dateTime'][:-6], '%Y-%m-%dT%H:%M:%S')
                    end = datetime.datetime.strptime(end['dateTime'][:-6], '%Y-%m-%dT%H:%M:%S')

                event_info = {"title": event.get("summary", None), 
                    "start": start, 
                    "end": end, 
                    "id": event.get("id", None),
                    "colorId": event.get("colorId", None),
                    "calendarId": calendarId
                }
                events_info.append(event_info)
            self.events_info = self.events_info + events_info
    
    def draw_calendar(self, config):
        event_width = config.width / 7
        event_height = config.height / (2 + 1 + (1 + config.event_num) * len(self.days))
        
        img = Image.new('RGBA', (config.width, config.height), 'white')
        img.putalpha(config.alpha)
        draw = ImageDraw.Draw(img)

        draw.rectangle([(0, 0), (config.width - 1, config.height - 1)], fill=None, outline='black')
        font = ImageFont.truetype('fonts/Lovelo-LineBold.otf', config.fontsize * 3)
        draw.text((config.width / 2, event_height), self.today.strftime('%B'), anchor='mm', font=font, fill='black')
        draw.line([(0, event_height * 2), (config.width, event_height * 2)], fill = 'black')

        for i in range(0,6):
            draw.line([(event_width * (i + 1), event_height * 2), (event_width * (i + 1), config.height)], fill = 'black')

        font = ImageFont.truetype(config.font, int(config.fontsize * 1.25))
        youbis = ['Mon', 'Tue', "Wed", 'Thu', 'Fri', 'Sat', 'Sun']
        for i, youbi in enumerate(youbis):
            draw.text((event_width * (0.5 + i), event_height * 2.5), youbi, anchor='mm', font=font, fill='black')

        for i, weekdays in enumerate(self.days):
            draw.line([(0, event_height * (i * (1 + config.event_num) + 3)), (config.width, event_height * (i * (1 + config.event_num) + 3))], fill='black')
            for j, day in enumerate(weekdays):
                draw.text((event_width * (0.5 + j), event_height * (i * (1 + config.event_num) + 3.5)), str(day.day), anchor='mm', font=font, fill='black', stroke_width=1, stroke_fill='white')
        
        font = ImageFont.truetype(config.font, config.fontsize)

        space=[0b0] * len(self.days)
        for event_info in self.events_info:
            start_date = event_info['start']
            end_date = event_info['end']
            if type(start_date) == datetime.datetime:
                start_date = datetime.date(start_date.year, start_date.month, start_date.day)
                end_date = datetime.date(end_date.year, end_date.month, end_date.day)
            for i, weekdays in enumerate(self.days):
                if not ((start_date < weekdays[0] and end_date < weekdays[0]) or (start_date > weekdays[6] and end_date > weekdays[6])):
                    start_index = 0
                    end_index = 6
                    for j, day in enumerate(weekdays):
                        if start_date == day:
                            start_index = j
                        if end_date == day:
                            end_index = j
                    event_period_in_week = end_index - start_index + 1

                    for j in range(0, config.event_num):
                        necessary_space = sum([2 ** (i + j * 7)for i in range(start_index, end_index + 1)])
                        if necessary_space & space[i] == 0:
                            space[i] = necessary_space | space[i]
                            left = event_width * start_index
                            right = event_width * (end_index + 1)
                            top = event_height * (4 + (config.event_num + 1) * i + j)
                            bottom = event_height * (4 + (config.event_num + 1) * i + j + 1)
                            if event_info["colorId"] != None:
                                color_bg = calendar_variance.color_dict["event"][event_info["colorId"]]["background"]
                                color_fg = calendar_variance.color_dict["event"][event_info["colorId"]]["foreground"]
                            else:
                                color_bg = calendar_variance.color_dict["event"]['1']["background"]
                                color_fg = calendar_variance.color_dict["event"]['1']["foreground"]

                            color_bg_RGBA = colorcode2RGB(color_bg)
                            color_bg_RGBA.append(config.alpha)
                            yuv = color_bg_RGBA[0] * 0.299 + color_bg_RGBA[1] * 0.587 + color_bg_RGBA[2] * 0.114
                            if yuv > 140:
                                color_fg = 'black'
                                color_stroke = 'white'
                            else:
                                color_fg = 'white'
                                color_stroke = 'black'

                            draw.rectangle([(left, top), (right, bottom)], fill=tuple(color_bg_RGBA), outline='black', width=1)

                            if event_info["title"] != None:
                                text = event_info["title"]
                            else:
                                text = ""
                            if type(event_info['start']) == datetime.datetime:
                                text = ' ' + event_info['start'].strftime('%H:%M') + " " + text
                            else:
                                text = ' ' + text
                            if draw.textsize(text, font=font)[0] > event_width * event_period_in_week:
                                while draw.textsize(text + "…", font=font)[0] > event_width * event_period_in_week:
                                    text = text[:-1]
                                text = text + "…"
                            draw.text((left, (top + bottom) / 2), text, fill=color_fg, stroke_width=1, stroke_fill=color_stroke, font=font, anchor='lm')
                            break
        return img

def colorcode2RGB(color_code):
    R = int(color_code[1:3], 16)
    G = int(color_code[3:5], 16)
    B = int(color_code[5:7], 16)
    return [R, G, B]

def run(calendarconf, creds):
    c = Calendar()
    c.OAuth2(creds)
    c.collect_events_info(calendarconf)
    img = c.draw_calendar(calendarconf)
    return img
