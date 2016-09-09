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

@app.route('/images/pull', methods=['POST'])
def image_puller():
    if not request.args.get('token') or not request.args.get('image'):
        return jsonify(success=False, error="Missing parameters"), 400

    image = request.args.get('image')

    if request.args.get('token') != os.environ.get('TOKEN'):
        return jsonify(success=False, error="Invalid token"), 403

    docker = Client(base_url='unix://var/run/docker.sock', timeout=5)

    old_containers = []
    for cont in docker.containers():
        cont_image = cont.get('Image')
        if image in cont_image:
            old_containers.append(cont)
            image = cont_image
            break

    if len(old_containers) is 0:
        return jsonify(success=False, error="No running containers found with the specified image"), 404

    image = image.split(':')
    image_name = image[0]
    image_tag  = image[1] if len(image) == 2 else 'latest'

    print 'Pulling new image...'
    docker.pull(image_name, tag=image_tag)

    print 'Creating new containers...'
    new_containers = []
    for cont in old_containers:
        new_cont = docker.create_container(image=cont.get('Image')) #volumes_from=cont_name
        new_containers.append(new_cont)

    print 'Stopping old containers...'
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
