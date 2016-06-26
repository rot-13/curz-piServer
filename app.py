import gevent
from gevent import monkey
monkey.patch_all()

import pychromecast as pycc
from websocket import create_connection
import time
import os
from subprocess import call

stream_server_ip = 'cpc-curz.herokuapp.com'
stream_server_port = 443
SOUND_FILES_PATH = '/home/pi/CPC/sounds/'
HTTP_URL = 'http://192.168.2.40:8000/'

CONTENT_TYPES = {
    'm4a': 'audio/m4a',
    'mp3': 'audio/mp3',
    'mp4': 'video/mp4'
}


def guess_content_type(extension):
    if extension in CONTENT_TYPES:
        return CONTENT_TYPES[extension]
    return 'audio/mp4'


def generate_mp3(text, lang="en"):
    filename = 'text_%s.mp3' % time.time()
    filename_on_disk = os.path.join(SOUND_FILES_PATH, filename)
    call("espeak -v %s \"%s\" --stdout | avconv -i - -ar 44100 -ac 2 -ab 192k -f mp3 %s > /dev/null 2>&1" % (lang, text, filename_on_disk), shell=True)
    return filename


def ping(ws):
    while ws.connected:
        gevent.sleep(5)
        ws.send('ping')


def run():
    ws = create_connection("wss://%s/connect" % (stream_server_ip))
    gevent.spawn(ping, ws)
    while ws.connected:
        gevent.sleep(0.1)
        recv_string = ws.recv()
        if recv_string == 'ping':
            continue
        elif recv_string.startswith('text:'):
            file_url = HTTP_URL + generate_mp3(recv_string[5:])
        else:
            file_url = recv_string
        extension = file_url.split('.')[-1]
        cast = pycc.get_chromecast(friendly_name="FloydCast")
        cast.media_controller.play_media(file_url, guess_content_type(extension))
        print "playing: " + file_url

    ws.close()

if __name__ == '__main__':
    while True:
        run()
        gevent.sleep(1)
