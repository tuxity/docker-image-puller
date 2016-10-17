Docker Image Puller
===================

[![](https://images.microbadger.com/badges/version/tuxity/docker-image-puller.svg)](https://hub.docker.com/r/tuxity/docker-image-puller/)
![](https://images.microbadger.com/badges/image/tuxity/docker-image-puller.svg)

## Overview

If you work with docker and continuous integrations tools, you might need to update your images on your servers as soon as your build is finished.

This tool is a tiny webserver listening for a `POST` and automatically update the specified image using [Docker](https://docs.docker.com/engine/reference/api/docker_remote_api/) API.

You just have to run the image on your server, and configure your CI tool.

CI tools to make the POST request:
- [Drone](http://readme.drone.io/plugins/webhook/)


## Installation

Launch the image on your server, where the images you want to update are
```
docker run -d \
  --name dip \
  --env TOKEN=abcd4242 \
  --env REGISTRY_USER=roberto \
  --env REGISTRY_PASSWD=robertopwd \
  -p 8080:8080 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  tuxity/docker-image-puller
```

Available env variable:
```
TOKEN*
REGISTRY_USER
REGISTRY_PASSWD
REGISTRY_URL (default: https://index.docker.io/v1/)
HOST (default: 0.0.0.0)
PORT (default: 8080)
DEBUG (default: False)
```

\* mandatory variables. For `TOKEN` You can generate a random string, it's a security measure.

After, you just have to make a request to the server:
```
POST http://ipofyourserver/images/pull?token=abcd4242&restart_containers=true&image=nginx:latest
```

## Logs

You can access container logs with
```
docker logs --follow dip
````
