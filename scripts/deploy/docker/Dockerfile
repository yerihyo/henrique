FROM ubuntu:18.04
MAINTAINER Foxytrixy "foxytrixy.bot@gmail.com"

ARG ENV

#ENV PATH /usr/local/bin:$PATH
#ENV LANG C.UTF-8
#ENV FLASK_APP henrique.main.run:app
#ENV FLASK_ENV development

RUN apt-get -y update
RUN apt-get -y dist-upgrade
RUN apt-get -y install build-essential libssl-dev libffi-dev nginx supervisor
RUN apt-get -y python3.6-dev python3-pip
#RUN apt-get -y install libpoppler-cpp-dev pkg-config

#COPY ./henrique/requirements.txt /henrique/henrique/requirements.txt

RUN pip install -U pip==20.02
RUN pip install -U setuptools==46.1.3
RUN pip install -U wheel==0.34.2
RUN pip install -r henrique/requirements.txt
RUN pip install -r scripts/deploy/requirements.server.txt

RUN scripts/deploy/uwsgi/compile.bash
RUN scripts/deploy/nginx/compile.bash
RUN touch /var/log/supervisor/supervisord.log

COPY . /henrique
# WORKDIR /henrique



#RUN cp -f /henrique/scripts/deploy/nginx/henrique /etc/nginx/sites-available/
#RUN rm -f /etc/nginx/sites-enabled/*
#RUN ln -sf /etc/nginx/sites-available/henrique /etc/nginx/sites-enabled/

#RUN cp -f /henrique/scripts/deploy/supervisor/super_uwsgi.conf /etc/supervisor/conf.d/

EXPOSE 80
EXPOSE 443

# CMD nginx; supervisord -n -c /henrique/scripts/deploy/supervisor/supervisord.conf

# enter
WORKDIR ${HOME}
ENTRYPOINT ["/henrique/scripts/deploy/docker/docker-entrypoint.sh"]
CMD ["supervisord", "-n", "-c", "/henrique/scripts/deploy/docker/supervisor/supervisord.conf"]
#CMD nginx; supervisord -n
