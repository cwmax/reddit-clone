FROM python:3.7-bullseye

RUN mkdir -p /usr/src/app && mkdir /usr/src/app/app
WORKDIR /usr/src/app

ADD ./requirements.txt /usr/src/app/requirements.txt

RUN pip install -r /usr/src/app/requirements.txt

COPY ./app /usr/src/app/app
COPY reddit_clone.py /usr/src/app

RUN ls -l /usr/src/app