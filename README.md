# Docker Image Puller [WIP]

## Overview

Tiny webserver listening for webhooks and automatically update a running docker image.


## Usage

```
docker run -d \
  --name dip \
  --env TOKEN=abcd4242 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  tuxity/docker-image-puller
```
