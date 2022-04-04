# A dockerfile for running the kgtk-browser
# python 3.9.7 is a KGTK 1.1.0 requirement
# this comes with a debian version 11 (bullseye)
FROM python:3.9.7

# Add graph-tool repository to the list of known apt sources
RUN echo "deb [ arch=amd64 ] https://downloads.skewed.de/apt bullseye main" >> /etc/apt/sources.list

# Fetch the public key in order to verify graph-tool
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-key 612DEFB798507F25

# update the registry
RUN apt-get update

# install graph-tool library for kgtk
RUN apt-get install python3-graph-tool -y

# install sqlite3 database
RUN apt-get install sqlite3 -y

RUN mkdir /src

COPY requirements.txt /src/requirements.txt

RUN pip install -r /src/requirements.txt

COPY kgtk_browser_app.py /src/
COPY properties_sort_metadata.json /src/
COPY browser/backend/ /src/browser/backend/
COPY app/ /src/app/

ARG FLASK_ENV=production
ENV FLASK_ENV=$FLASK_ENV

ARG FLASK_APP=kgtk_browser_app.py
ENV FLASK_APP=$FLASK_APP

ARG KGTK_BROWSER_CONFIG=browser/backend/kgtk_browser_config.py
ENV KGTK_BROWSER_CONFIG=$KGTK_BROWSER_CONFIG

WORKDIR /src
