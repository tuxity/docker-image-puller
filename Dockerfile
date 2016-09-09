FROM python:2.7-slim
MAINTAINER Kévin Darcel <kevin.darcel@gmail.com>

WORKDIR /usr/src/docker-image-updater

COPY app.py requirements.txt /usr/src/docker-image-updater/

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python", "app.py"]
