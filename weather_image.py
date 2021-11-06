from urllib import request
import json
from PIL import Image, ImageDraw, ImageFont
import cairosvg
import os

class Weather:
    weatherCodes = None
    temp = None
    pops = None
    def get_forecast(self, config):
        url = 'https://www.jma.go.jp/bosai/forecast/data/forecast/' + config.office_code + '.json'
        request.urlretrieve(url, 'forecast.json')
        with open('forecast.json', 'r', encoding='UTF-8') as f:
            forecast_data = json.load(f)  

        timepoint = forecast_data[0]['timeSeries'][0]['timeDefines']
        for i in forecast_data[0]['timeSeries'][0]['areas']:
            if i['area']['code'] == config.area_code:
                weatherCodes = i['weatherCodes']
                break
        self.weatherCodes = dict(zip(timepoint, weatherCodes))

        self.pops = {}
        timepoint = forecast_data[0]['timeSeries'][1]['timeDefines']
        timepoint = [i[0:10] for i in timepoint]
        for i in forecast_data[0]['timeSeries'][1]['areas']:
            if i['area']['code'] == config.area_code:
                pops = i['pops']
        for time, pop in zip(timepoint, pops):
            if time not in self.pops.keys():
                self.pops[time] = []
            self.pops[time].append(pop)

        timepoint = forecast_data[1]['timeSeries'][0]['timeDefines']
        timepoint = [i[0:10] for i in timepoint]
        for i in forecast_data[1]['timeSeries'][0]['areas']:
            if i['area']['code'] == config.area_code:
                pops = i['pops']
        for time, pop in zip(timepoint, pops):
            if time not in self.pops.keys():
                self.pops[time] = pop
        
        timepoint = forecast_data[1]['timeSeries'][1]['timeDefines']
        temp = zip(forecast_data[1]['timeSeries'][1]['areas'][0]['tempsMin'], forecast_data[1]['timeSeries'][1]['areas'][0]['tempsMax'])
        self.temp = dict(zip(timepoint, temp))

    def draw_forecast(self, config):
        self.download_icon()

        img = Image.new('RGBA', (config.width, config.height), 'white')
        img.putalpha(config.alpha)
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(config.font, config.fontsize)
        period = len(self.weatherCodes)

        x_stroke = config.width / len(self.weatherCodes)
        area_width, area_height = draw.textsize(config.office + config.area, font=font)
        y_stroke = (config.height - area_height - config.icon_height) / 4

        draw.rectangle((0, 0, config.width, config.height), fill=None, outline='black')
        # draw.rectangle((0, 0, config.width - 1, config.height - 1), fill=None, outline='black')

        draw.text((1, 0), config.office + config.area, fill='black', font=font, stroke_width=1, stroke_fill='white')

        x_pops = config.width / len(self.weatherCodes) / 2
        y_pops = y_stroke + 10
        font_pop = ImageFont.truetype(config.font, int(config.fontsize*0.9))
        for i in list(self.pops.values())[0:period]:
            if type(i) is list:
                text = '/'.join(['-']*(4-len(i)) + i)
            else:
                text = i
            text = text + '%'
            draw.text((x_pops, y_pops), text, fill='black', anchor = 'mt', font=font_pop, stroke_width=1, stroke_fill='white')
            x_pops += x_stroke

        x_temp = config.width / len(self.weatherCodes) / 2
        y_temp = y_pops + y_stroke
        for i in list(self.temp.values())[0:period]:
            temp = '{}/{}℃'.format(i[0], i[1])
            draw.text((x_temp, y_temp), temp, fill='black', anchor='mt', font=font, stroke_width=1, stroke_fill='white')
            x_temp += x_stroke

        x_icon = config.width / len(self.weatherCodes) / 2 - config.icon_width / 2
        y_icon = y_temp + y_stroke
        for i in self.weatherCodes.values():
            pngname = 'icon/' + i + '.png'
            icon = Image.open(pngname)
            icon = icon.resize((config.icon_width, config.icon_height))
            img.paste(icon, (int(x_icon), int(y_icon)), icon)
            x_icon += x_stroke
        x_date = config.width / len(self.weatherCodes) / 2
        y_date = y_icon + config.icon_height
        for i in self.weatherCodes.keys():
            date = '{}/{}'.format(i[5:7], i[8:10])
            draw.text((x_date, y_date), date, fill='black', anchor='mt', font=font, stroke_width=1, stroke_fill='white')
            x_date += x_stroke
        return img

    def download_icon(self):
        os.makedirs('icon', exist_ok=True)
        for i in self.weatherCodes.values():
            svgname = 'icon/' + i + '.svg'
            pngname = 'icon/' + i + '.png'
            try:
                url = 'https://www.jma.go.jp/bosai/forecast/img/' + i + '.svg'
                request.urlretrieve(url, svgname)
                cairosvg.svg2png(url=svgname, write_to=pngname)
            except:
                img_error = Image.new('RGBA', (80, 60))
                img_error.save(pngname)

def run(weatherconf):
    weather_now = Weather()
    weather_now.get_forecast(weatherconf)
    img = weather_now.draw_forecast(weatherconf)
    return img