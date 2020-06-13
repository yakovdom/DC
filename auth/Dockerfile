FROM python:latest

ADD auth/requirements.txt /app/
RUN apt-get update \
    && apt-get clean \
    && apt-get update -qqq \
    && pip install --upgrade pip \ 
    && pip install -r /app/requirements.txt

ADD auth/*.py /auth/
ADD config/*.py /auth/
ADD config/*.json /
ADD protos/*.py /auth/

#WORKDIR ../auth/
