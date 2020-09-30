FROM ubuntu:20.04
MAINTAINER Foxytrixy "foxytrixy.bot@gmail.com"

#ARG ENV

#ENV PATH /usr/local/bin:$PATH
#ENV LANG C.UTF-8
#ENV FLASK_APP henrique.main.run:app
#ENV FLASK_ENV development
ENV TZ=America/Los_Angeles
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

###################
# aptitude
###################
RUN apt-get -y update
RUN apt-get -y dist-upgrade
RUN apt-get -y install build-essential libssl-dev libffi-dev nginx supervisor git
RUN apt-get -y install python3.8 python3-pip
#RUN apt-get -y install libpoppler-cpp-dev pkg-config

###################
# pip
###################
RUN pip3 install --index-url https://pypi.python.org/simple/ --upgrade pip==20.0.2
#RUN pip3 install -U pip==20.0.2
RUN pip3 install -U setuptools==46.1.3
RUN pip3 install -U wheel==0.34.2

COPY ./henrique/requirements.txt /app/henrique/requirements.txt
RUN pip3 install -r /app/henrique/requirements.txt

COPY ./scripts/deploy/requirements.server.txt /app/scripts/deploy/requirements.server.txt
RUN pip3 install -r /app/scripts/deploy/requirements.server.txt


###################
# uwsgi / nginx
###################
#COPY ./scripts/deploy/uwsgi /app/scripts/deploy/uwsgi
#RUN /app/scripts/deploy/uwsgi/compile.bash

#COPY ./scripts/deploy/nginx /app/scripts/deploy/nginx
#RUN /app/scripts/deploy/nginx/compile.bash

EXPOSE 80 443

#RUN mkdir -p /var/log /run/pid && \
#    chmod -R 777 /var/log /run /run /run/pid && \
#    chgrp -R 0 /var/log /run /run /run/pid && \
#    chmod -R g+rwX /var/log /run /run /run/pid

#    rm /etc/nginx/conf.d/default.conf

#RUN mkdir -p /app/run/pid
#RUN mkdir -p /app/log/supervisor
#RUN touch /app/log/supervisor/supervisord.log

RUN mkdir -p /var/log/supervisor /var/log/nginx /run/pid && \
    chmod -R 777 /var/log /run && \
    chgrp -R 0 /var/log /run  && \
    chmod -R g+rwX /var/log /run

#RUN mkdir -p /run/pid /run/uwsgi
#RUN mkdir -p /var/log/supervisor
#RUN touch /var/log/supervisor/supervisord.log

RUN set -x ; id -g www-data &>/dev/null || addgroup --gid 82 www-data && exit 0 ; exit 1
RUN set -x ; id -u www-data &>/dev/null || adduser --uid 82 --group www-data www-data && exit 0 ; exit 1

# supervisord does it not?
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
	&& ln -sf /dev/stderr /var/log/nginx/error.log

#RUN touch /run/pid/supervisord.pid
#RUN touch /run/supervisor.sock

#RUN cp -f /app/scripts/deploy/nginx/app /etc/nginx/sites-available/
#RUN rm -f /etc/nginx/sites-enabled/*
#RUN ln -sf /etc/nginx/sites-available/app /etc/nginx/sites-enabled/

#RUN cp -f /app/scripts/deploy/supervisor/super_uwsgi.conf /etc/supervisor/conf.d/

# enter

COPY . /app
WORKDIR /app
ENTRYPOINT ["/app/scripts/deploy/docker/docker-entrypoint.bash"]
# CMD ["supervisord", "-n", "-c", "/app/henrique/main/singleton/deploy/supervisord/conf/henrique.supervisord.prod.conf"]
#CMD nginx; supervisord -n
