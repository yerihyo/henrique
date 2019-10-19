FROM python:3.7
MAINTAINER foxytrixy foxytrixy.bot@gmail.com

ARG ENV

# Environments 설정
ENV PATH /usr/local/bin:$PATH
ENV LANG C.UTF-8
ENV FLASK_APP henrique.main.run
ENV FLASK_ENV development

# apt-get으로 nginx, supervisor 설치
RUN apt-get -y update
RUN apt-get -y dist-upgrade
RUN apt-get -y install build-essential libssl-dev libffi-dev nginx supervisor

COPY . /henrique
WORKDIR /henrique

RUN pip install --upgrade pip
RUN pip install -r henrique/requirements.txt
RUN pip install -r scripts/deploy/requirements.server.txt

# henrique.ini(uwsgi config) jinja로 생성
RUN /henrique/scripts/deploy/uwsgi/run.bash

# henrique(nginx config) jinja로 생성
RUN /henrique/scripts/deploy/nginx/run.bash

# nginx 설정 파일 복사 및 링크
RUN cp -f /henrique/scripts/deploy/nginx/henrique /etc/nginx/sites-available/
RUN rm -f /etc/nginx/sites-enabled/*
RUN ln -sf /etc/nginx/sites-available/henrique /etc/nginx/sites-enabled/

# supervisor 설정 파일 복사
RUN cp -f /henrique/scripts/deploy/supervisor/super_uwsgi.conf /etc/supervisor/conf.d/

# http port
EXPOSE 80
# https port
EXPOSE 443

# pkill nginx후 supervisord -n 실행
CMD nginx; supervisord -n
