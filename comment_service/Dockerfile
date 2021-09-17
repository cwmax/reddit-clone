FROM python:3.7

RUN mkdir -p /usr/src/app/comment_service
WORKDIR /usr/src/app

ADD ./requirements.txt /usr/src/app/requirements.txt

RUN pip install -r /usr/src/app/requirements.txt

COPY ./comment_service /usr/src/app/comment_service