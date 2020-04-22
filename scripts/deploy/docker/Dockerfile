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
RUN apt-get -y install python3.6 python3-pip
#RUN apt-get -y install libpoppler-cpp-dev pkg-config

COPY ./henrique/requirements.txt /app/henrique/requirements.txt
COPY ./henrique/scripts/deploy/requirements.server.txt /app/henrique/requirements.txt
RUN pip3 install --index-url https://pypi.python.org/simple/ --upgrade pip==20.0.2
#RUN pip3 install -U pip==20.0.2
RUN pip3 install -U setuptools==46.1.3
RUN pip3 install -U wheel==0.34.2
RUN pip3 install -r /app/henrique/requirements.txt
RUN pip3 install -r /app/scripts/deploy/requirements.server.txt

COPY ./scripts/deploy/uwsgi/compile.bash /app/scripts/deploy/uwsgi/compile.bash
COPY ./scripts/deploy/nginx/compile.bash /app/scripts/deploy/nginx/compile.bash
RUN scripts/deploy/uwsgi/compile.bash
RUN scripts/deploy/nginx/compile.bash
RUN touch /var/log/supervisor/supervisord.log

COPY . /app
# WORKDIR /app



#RUN cp -f /app/scripts/deploy/nginx/app /etc/nginx/sites-available/
#RUN rm -f /etc/nginx/sites-enabled/*
#RUN ln -sf /etc/nginx/sites-available/app /etc/nginx/sites-enabled/

#RUN cp -f /app/scripts/deploy/supervisor/super_uwsgi.conf /etc/supervisor/conf.d/

EXPOSE 80
EXPOSE 443

# CMD nginx; supervisord -n -c /app/scripts/deploy/supervisor/supervisord.conf

# enter
WORKDIR ${HOME}
ENTRYPOINT ["/app/scripts/deploy/docker/docker-entrypoint.sh"]
CMD ["supervisord", "-n", "-c", "/app/scripts/deploy/docker/supervisor/supervisord.conf"]
#CMD nginx; supervisord -n
