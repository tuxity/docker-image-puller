#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import click
import re

from flask import Flask
from flask import request
from flask import jsonify

import docker

app = Flask(__name__)
client = docker.from_env()

@app.route('/')
def main():
    return jsonify(success=True), 200

@app.route('/images/pull', methods=['POST'])
def image_puller():
    if not request.form['token'] or not request.form['image']:
        return jsonify(success=False, error="Missing parameters"), 400

    image = request.form['image']

    if request.form['token'] != os.environ['TOKEN']:
        return jsonify(success=False, error="Invalid token"), 403

    restart_containers = True if request.form['restart_containers'] == "true" else False

    old_containers = []
    for container in client.containers.list():
        if re.match( r'.*' + re.escape(image) + r'$', container.attrs['Config']['Image']):
            old_containers.append(container)

    if len(old_containers) == 0:
        return jsonify(success=False, error="No running containers found with the specified image"), 404

    print ('Updating', str(len(old_containers)), 'containers with', image, 'image')
    image = image.split(':')
    image_name = image[0]
    image_tag  = image[1] if len(image) == 2 else 'latest'

    print ('\tPulling new image...')
    client.images.pull(image_name, tag=image_tag)

    if restart_containers == False:
        return jsonify(success=True, message=str(len(old_containers)) + " containers updated"), 200

    print ('\tCreating new containers...')
    new_containers = []
    for container in old_containers:
        if 'HOSTNAME' in os.environ and os.environ['HOSTNAME'] == container.attrs['Id']:
            return jsonify(success=False, error="You can't restart the container where the puller script is running"), 403

        new_cont = docker.APIClient().create_container(container.attrs['Config']['Image'], environment=container.attrs['Config']['Env'], host_config=container.attrs['HostConfig'])
        
        new_containers.append(client.containers.get(new_cont['Id']))

    print ('\tStopping old containers...')
    for container in old_containers:
        container.stop()

    print ('\tStarting new containers...')
    for container in new_containers:
        container.start()

    print ('\tRemoving old containers...')
    for container in old_containers:
        container.remove()

    return jsonify(success=True, message=str(len(old_containers)) + " containers updated and restarted"), 200

@click.command()
@click.option('-h',      default='0.0.0.0', help='Set the host')
@click.option('-p',      default=8080,      help='Set the listening port')
@click.option('--debug', default=False,     help='Enable debug option')
def main(h, p, debug):
    if not os.environ.get('TOKEN'):
        print ('ERROR: Missing TOKEN env variable')
        sys.exit(1)

    registry_user = os.environ.get('REGISTRY_USER')
    registry_passwd = os.environ.get('REGISTRY_PASSWD')
    registry_url = os.environ.get('REGISTRY_URL', 'https://index.docker.io/v1/')

    if registry_user and registry_passwd:
        try:
            client.login(username=registry_user, password=registry_passwd, registry=registry_url)
        except Exception as e:
            print(e)
            sys.exit(1)

    app.run(
        host  = os.environ.get('HOST', default=h),
        port  = os.environ.get('PORT', default=p),
        debug = os.environ.get('DEBUG', default=debug)
    )

if __name__ == "__main__":
    main()
