FROM ubuntu:18.04

RUN apt-get update -y
RUN apt-get install -y git python3-pip curl
RUN python3 -m pip install --upgrade pip pytest-cov nbval ipywidgets\
      git+git://github.com/joommf/oommfodt.git \
      git+git://github.com/joommf/discretisedfield.git

WORKDIR /usr/local
COPY . /usr/local/micromagneticdata/
WORKDIR /usr/local/micromagneticdata
RUN python3 -m pip install .
