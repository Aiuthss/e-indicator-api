import calendar_image
import weather_image
import tasks_image
import config
import random
import requests
from PIL import Image
import logging
from googleapiclient.discovery import build

def quantize(image):
    logger = logging.getLogger(__name__)
    # Create a pallette with the 7 colors supported by the panel
    pal_image = Image.new("P", (1,1))
    pal_image.putpalette( (0,0,0,  255,255,255,  0,255,0,   0,0,255,  255,0,0,  255,255,0, 255,128,0) + (0,0,0)*249)
    # Check if we need to rotate the image
    imwidth, imheight = image.size
    if(imwidth == image.width and imheight == image.height):
        image_temp = image
    elif(imwidth == image.height and imheight == image.width):
        image_temp = image.rotate(90, expand=True)
    else:
        logger.warning("Invalid image dimensions: %d x %d, expected %d x %d" % (imwidth, imheight, image.width, image.height))
    image_7color = image_temp.convert("RGB").quantize(palette=pal_image)
    return image_7color

def bg_draw(config):
    if config.bg_src == 'Google_Photo':
        img = Image.open('background.bmp')
    else:
        img = Image.new('RGBA', (config.width, config.height), 'white')


    if config.bg_fmt == 'full_screen':
        wc = img.width / 2
        hc = img.height / 2
        if img.width / config.width < img.height / config.height:
            wcrop = img.width
            hcrop = img.width * config.height / config.width
        else:
            hcrop = img.height
            wcrop = img.height * config.width / config.height
        img = img.crop((int(wc - wcrop / 2), int(hc - hcrop / 2), int(wc + wcrop / 2), int(hc + hcrop / 2)))
        img = img.resize((config.width, config.height))
    elif config.bg_fmt == 'whole_image':
        bg_margin = Image.new(img.mode, (config.width, config.height), config.bg_color)
        if img.width / config.width > img.height / config.height:
            w = config.width
            h = config.width * img.height / img.width
            x = 0
            y = (config.height - h) / 2
        else:
            h = config.height
            w = config.height * img.width / img.height
            x = (config.width - w) / 2
            y = 0
        img = img.resize((int(w), int(h)))
        bg_margin.paste(img, (int(x), int(y)))
        img = bg_margin
    else:
        print('invalid background format specified')
        img = img.resize((config.width, config.height))
    return img

def save_bg_img(creds, albumIds=None, baseUrl=None):
    service = build('photoslibrary', 'v1', credentials=creds, static_discovery=False)

    if not baseUrl:
        if not albumIds:
            albums_list = service.albums().list().execute().get('albums', None)
            albumIds = [i['id'] for i in albums_list]

        mediaItem_list = []
        for albumId in albumIds:
            body = {'albumId': albumId}
            x = service.mediaItems().search(body=body).execute().get('mediaItems', None)
            mediaItem_list = mediaItem_list + x
        baseUrls = [i['baseUrl'] for i in mediaItem_list if 'photo' in i['mediaMetadata'].keys()]
        baseUrl = random.choice(baseUrls)

    response = requests.get(baseUrl)
    with open('background.bmp', 'wb') as f:
        f.write(response.content)

def run(config_file):
    conf = config.Config(config_file)
    if conf.general.bg_src == 'Google_Photo':
        save_bg_img(conf.google.creds, albumIds=conf.general.albumIds, baseUrl=conf.general.baseUrl)

    img = bg_draw(conf.general)

    for i in conf.general.contents:
        if i == 'weather':
            weather_img = weather_image.run(conf.weather)
            img.paste(weather_img, (conf.weather.x, conf.weather.y), weather_img)
        elif i == 'calendar':
            calendar_img = calendar_image.run(conf.calendar, conf.google.creds)
            img.paste(calendar_img, (conf.calendar.x, conf.calendar.y), calendar_img)
        elif i == 'tasks':
            tasks_img = tasks_image.run(conf.tasks, conf.google.creds)
            img.paste(tasks_img, (conf.tasks.x, conf.tasks.y), tasks_img)
    img = quantize(img)
    return img