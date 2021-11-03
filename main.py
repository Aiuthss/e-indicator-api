import image_generator
from flask import Flask, request, send_file
import os
import json

app = Flask(__name__)
app.logger.debug('debug')
app.logger.info('info')
app.logger.warning('message')
app.logger.error('error')
app.logger.critical('critical')

@app.route('/', methods=['POST'])
def post_img():
    data = json.loads(request.get_data().decode('utf-8'))
    with open('config.json', 'w') as f:
        f.write(json.dumps(data['config']))
    with open('token.json', 'w') as f:
        f.write(json.dumps(data['access_token']))

    img_7color = image_generator.run('config.json')
    buffer = getbuffer(img_7color)
    # buffer_str = '\n'.join([str(i) for i in buffer])
    with open('buffer.txt', 'wb') as f:
        f.write(bytes(buffer))
    return bytes(buffer)

@app.route('/preview', methods=['POST'])
def preview():
    data = json.loads(request.get_data().decode('utf-8'))
    with open('config.json', 'w') as f:
        f.write(json.dumps(data['config']))
    with open('token.json', 'w') as f:
        f.write(json.dumps(data['access_token']))

    img_7color = image_generator.run('config.json')
    img_7color.save('preview.bmp')
    return send_file('preview.bmp')

@app.route('/test', methods=['POST'])
def repeat():
    data = request.get_data()
    return data

def getbuffer(image):
    buf_7color = bytearray(image.tobytes('raw'))
    buf = [0x00] * int(image.width * image.height / 2)
    idx = 0
    # 4 bit * 2 pixel = 1 byte
    for i in range(0, len(buf_7color), 2):
        buf[idx] = (buf_7color[i] << 4) + buf_7color[i+1]
        idx += 1
    return buf

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))