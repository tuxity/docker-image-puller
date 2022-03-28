FROM python:3.10-alpine
LABEL maintainer="Kévin Darcel <tuxity@users.noreply.github.com>"

WORKDIR /usr/src/docker-image-updater

COPY app.py requirements.txt /usr/src/docker-image-updater/

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python", "-u", "app.py"]
