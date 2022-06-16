from flask import Flask
import logging
import os
import click

app = Flask("")
app.logger.disabled = True # for some reason it logs pynacl is not installed everytime on startup?
os.environ['WERKZEUG_RUN_MAIN'] = 'true'
log = logging.getLogger('werkzeug')
#log.setLevel(logging.ERROR)
log.disabled = True

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
