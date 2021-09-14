FROM python:3.7

RUN mkdir -p /usr/src/app/tests
WORKDIR /usr/src/app/tests

ADD ./requirements.txt /usr/src/app/requirements.txt

RUN pip install -r /usr/src/app/requirements.txt

COPY ./main_app_tests /usr/src/app/tests