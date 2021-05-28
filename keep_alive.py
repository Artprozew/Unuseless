# import os
# from flask import Flask, request, Response
# from flask_socketio import SocketIO
# from threading import Thread
# import sys
# import click
# import time

# scrtpt = os.environ['scrtpt']
# scrtsckt = os.environ['scrtsckt']

# app = Flask(__name__)
# app.config['SECRET_KEY'] = scrtsckt
# socketio = SocketIO(app)


# @app.route(scrtpt, methods=['POST'])
# def respond():
#     print(request.json['username'] + ' : ' + request.json['content'])
#     return Response(status=200)


# @app.route('/')
# def main():
#     return 'Your bot is alive!'

# '''class RunInBackground(object):
#     def __init__(self, interval=1):
#         self.interval = interval
#         server = Thread(target=self.run)
#         server.daemon = True
#         server.start()

#     def run(self):
#         while True:'''
#             #time.sleep(self.interval)
# def run():
#     socketio.run(app)
#     app.run(host='0.0.0.0', port=8080)


# def keep_alive():
#     server = Thread(target=run)
#     server.start()
from flask import Flask
import logging
import os
import click

app = Flask("")

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
log.disabled = True
#app.logger.disabled = True # for some reason it logs pynacl is not installed everytime on startup
os.environ['WERKZEUG_RUN_MAIN'] = 'true'

def secho(text, file=None, nl=None, err=None, color=None, **styles):
    pass

def echo(text, file=None, nl=None, err=None, color=None, **styles):
    pass

click.echo = echo
click.secho = secho


@app.route("/")
def home():
  return "Keep Alive"


def run():
  app.run(host="0.0.0.0")

