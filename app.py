#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import click
import json

from flask import Flask
from flask import request
from flask import jsonify

from docker import Client

app = Flask(__name__)

@app.route('/')
def main():
    return jsonify(success=True, data=[]), 200

@app.route('/images/<image>/pull', methods=['POST'])
def image_puller(image):
    if request.args.get('token') != os.environ.get('TOKEN'):
        return jsonify(success=False, error="Invalid token"), 403

    docker = Client(base_url='unix://var/run/docker.sock', timeout=5)

    image_name = ''
    old_containers = []
    for cont in docker.containers():
        if image in cont.get('Image'):
            old_containers.append(cont)
            if not image_name:
                image_name = cont.get('Image')

    if len(old_containers) is 0:
        return jsonify(success=False, error="No containers found"), 404

    # print 'Pulling image...'
    # print containers[0]
    # for line in docker.pull(image_name, stream=True):
    #     print json.dumps(json.loads(line), indent = 4)

    print 'Creating containers...'
    new_containers = []
    for cont in old_containers:
        new_cont = docker.create_container(image=cont.get('Image')) #volumes_from=cont_name
        new_containers.append(new_cont)

    print 'Stopping containers...'
    for cont in old_containers:
        docker.stop(container=cont.get('Id'))

    print 'Starting new containers...'
    for cont in new_containers:
        docker.start(container=cont.get('Id'))

    print 'Removing old containers...'
    for cont in old_containers:
        docker.remove_container(container=cont.get('Id'))

    return jsonify(success=True, data=new_containers), 200

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
