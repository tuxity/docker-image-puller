#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import click

from flask import Flask
from flask import request
from flask import jsonify

from docker import Client

app = Flask(__name__)

@app.route("/")
def main():
    return jsonify(success=True, data=[]), 200

@app.route("/hooks/<hook>", methods=['POST'])
def hook_listen(hook):
    if request.args.get('token') != os.environ.get('TOKEN'):
        return jsonify(success=False, error="Invalid token"), 403

    docker = Client(base_url='unix://var/run/docker.sock', timeout=10)

    return jsonify(success=True, data=docker.containers()), 200

@click.command()
@click.option('-h',      default = 'localhost', help = 'Set the host')
@click.option('-p',      default = 8080,        help = 'Set port on which we have to listen')
@click.option('--debug', default = False,       help = 'Enable debug option')
def main(h, p ,debug):
    if not os.environ.get('TOKEN'):
        print 'ERROR: Missing TOKEN env variable'
        sys.exit(0)

    app.run(
        host  = os.environ.get('HOST')  if os.environ.get('HOST')  else h,
        port  = os.environ.get('PORT')  if os.environ.get('PORT')  else p,
        debug = os.environ.get('DEBUG') if os.environ.get('DEBUG') else debug
    )

if __name__ == "__main__":
    main()
