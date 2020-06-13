FROM python:latest

ADD push/requirements.txt /app/
RUN apt-get update \
    && apt-get clean \
    && apt-get update -qqq \
    && pip install --upgrade pip \ 
    && pip install -r /app/requirements.txt

ADD push/*.py /push/
ADD config/*.py /push/
ADD config/*.json /
ADD protos/*.py /push/
