FROM ubuntu:18.04
MAINTAINER Foxytrixy "foxytrixy.bot@gmail.com"

ARG ENV

# ENV PATH /usr/local/bin:$PATH
ENV LANG C.UTF-8
ENV FLASK_APP henrique.main.run
ENV FLASK_ENV development

RUN apt-get -y update
RUN apt-get -y dist-upgrade
RUN apt-get -y install python3.5 python3-dev python3-pip build-essential libssl-dev libffi-dev nginx supervisor

COPY ./henrique/requirements.txt /app/henrique/requirements.txt

RUN pip3 install -U pip3==20.02
RUN pip3 install -U setuptools==46.1.3
RUN pip3 install -U wheel==0.34.2
RUN pip3 install -r henrique/requirements.txt


COPY . /app
WORKDIR /app

RUN /henrique/scripts/deploy/uwsgi/run.bash
RUN /henrique/scripts/deploy/nginx/run.bash

RUN cp -f /henrique/scripts/deploy/nginx/henrique /etc/nginx/sites-available/
RUN rm -f /etc/nginx/sites-enabled/*
RUN ln -sf /etc/nginx/sites-available/henrique /etc/nginx/sites-enabled/

RUN cp -f /henrique/scripts/deploy/supervisor/super_uwsgi.conf /etc/supervisor/conf.d/

EXPOSE 80
EXPOSE 443

CMD nginx; supervisord -n
