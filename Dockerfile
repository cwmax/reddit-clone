FROM python:3.7

RUN mkdir -p /usr/src/app/app
WORKDIR /usr/src/app

ADD ./requirements.txt /usr/src/app/requirements.txt

RUN pip install -r /usr/src/app/requirements.txt

COPY reddit_clone.py /usr/src/app
COPY ./app /usr/src/app/app