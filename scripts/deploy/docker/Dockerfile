FROM python:3.7
MAINTAINER kycho kycho@lbox.kr

ARG ENV

# Environments 설정
ENV PATH /usr/local/bin:$PATH
ENV LANG C.UTF-8
ENV FLASK_APP delphi.app.main.run
ENV FLASK_ENV development

# apt-get으로 nginx, supervisor 설치
RUN apt-get -y update
RUN apt-get -y dist-upgrade
RUN apt-get -y install build-essential libssl-dev libffi-dev nginx supervisor python3.7-dev libpoppler-cpp-dev pkg-config

COPY . /delphi
WORKDIR /delphi

RUN pip install --upgrade pip
RUN pip install -r delphi/requirements.txt
RUN pip install -r scripts/deploy/requirements.server.txt

# delphi.ini(uwsgi config) jinja로 생성
RUN /delphi/scripts/deploy/uwsgi/run.bash

# delphi(nginx config) jinja로 생성
RUN /delphi/scripts/deploy/nginx/run.bash

# nginx 설정 파일 복사 및 링크
RUN cp -f /delphi/scripts/deploy/nginx/delphi /etc/nginx/sites-available/
RUN rm -f /etc/nginx/sites-enabled/*
RUN ln -sf /etc/nginx/sites-available/delphi /etc/nginx/sites-enabled/

# supervisor 설정 파일 복사
RUN cp -f /delphi/scripts/deploy/supervisor/super_uwsgi.conf /etc/supervisor/conf.d/

# http port
EXPOSE 80
# https port
EXPOSE 443

# pkill nginx후 supervisord -n 실행
CMD nginx; supervisord -n
