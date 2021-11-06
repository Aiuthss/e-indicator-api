import os
import json
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from PIL import Image, ImageDraw, ImageFont

class Tasks:
    def OAuth2(self, creds):
        self.service = build('tasks', 'v1', credentials=creds)

    def collect_tasks_info(self, config):
        tasklists_info = {}
        for tasklistId in config.tasklistIds:
            result = self.service.tasklists().get(tasklist=tasklistId).execute()
            list_title = result.get('title', None)
            result = self.service.tasks().list(tasklist=tasklistId).execute()
            tasks = result.get('items', None)
            parents_list = [None]*30
            child_dict = {}
            for task in tasks:
                title = task['title']
                id = task['id']
                parent = task.get('parent', None)
                position = int(task['position'])
                if parent:
                    if parent not in child_dict.keys():
                        child_dict[parent] = [None]*20    
                    child_dict[parent][position] = title
                else:
                    parents_list[position] = (title, id)

            tasklist_info = []
            for parent in parents_list:
                if parent:
                    parent_title = parent[0]
                    id = parent[1]
                    childs = child_dict.get(id, None)
                    if childs:
                        childs = [child for child in childs if child]
                    tasklist_info.append((parent_title, childs))

            tasklists_info[list_title] = tasklist_info
        self.tasklists_info = tasklists_info

    def write_tasks(self, config):
        img = Image.new('RGBA', (config.width, config.height), 'white')
        img.putalpha(config.alpha)
        draw = ImageDraw.Draw(img)
        draw.rectangle((0, 0, config.width, config.height), fill=None, outline='black')
        x = 5
        y = 0
        for list_title, tasks in self.tasklists_info.items():
            font = ImageFont.truetype(config.font, int(config.fontsize*1.25))
            draw_underlined_text(draw, (x, y), list_title, font=font, fill='black', stroke_width=1, stroke_fill='white')
            y += config.fontsize*1.75
            for task in tasks:
                parent = task[0]
                childs = task[1]
                font = ImageFont.truetype(config.font, config.fontsize)
                draw.text((x, y), '□'+parent, font=font, fill='black', stroke_width=1, stroke_fill='white')
                y += config.fontsize*1.5
                if childs:
                    for child in childs:
                        draw.text((x+10, y), '□'+child, font=font, fill='black', stroke_width=1, stroke_fill='white')
                        y += config.fontsize*1.5
        return img

def draw_underlined_text(draw, pos, text, font, **options):    
    twidth, theight = draw.textsize(text, font=font)
    lx, ly = pos[0], pos[1] + theight
    draw.text(pos, text, font=font, **options)
    draw.line((lx, ly, lx + twidth, ly), fill='black')
    
def run(tasksconf, creds):
    t = Tasks()
    t.OAuth2(creds)
    t.collect_tasks_info(tasksconf)
    img = t.write_tasks(tasksconf)
    return img
