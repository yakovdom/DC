FROM python:latest

ADD server/requirements.txt /app/
RUN apt-get update \
    && apt-get clean \
    && apt-get update -qqq \
    && pip install --upgrade pip \ 
    && pip install -r /app/requirements.txt

ADD server/*.py /server/
ADD config/*.py /server/
ADD config/*.json /
ADD protos/*.py /server/

# WORKDIR /server/
