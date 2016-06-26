import pychromecast as pycc
from websocket import create_connection

stream_server_ip = 'cpc-curz.herokuapp.com'
# stream_server_ip = '127.0.0.1'
stream_server_port = 443

CONTENT_TYPES = {
    'm4a': 'audio/m4a',
    'mp3': 'audio/mp3',
    'mp4': 'video/mp4'
}


def guess_content_type(extension):
    if extension in CONTENT_TYPES:
        return CONTENT_TYPES[extension]
    return 'audio/mp4'


def run():
    ws = create_connection("wss://%s/connect" % (stream_server_ip))
    while ws.connected:
        file_url = ws.recv()
        extension = file_url.split('.')[-1]
        cast = pycc.get_chromecast(friendly_name="FloydCast")
        cast.media_controller.play_media(file_url, guess_content_type(extension))
        print "got: " + file_url

    ws.close()

if __name__ == '__main__':
    run()