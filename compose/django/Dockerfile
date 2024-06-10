# pull official base image
FROM python:3.11.3

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2
RUN apt-get update \
  && apt-get -y install netcat gcc postgresql \
  && apt-get clean \
  && pip install psycopg2-binary

# install dependencies
RUN pip install --upgrade pip
COPY ./app/requirements.txt /usr/src/app/requirements.txt
RUN pip install -r /usr/src/app/requirements.txt


# copy project
COPY ./app /usr/src/app/
COPY ./compose /usr/src/app/compose

RUN chmod +x /usr/src/app/compose/django/entrypoint.sh

COPY ./compose/django/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

# COPY ./compose/django/celery/worker/start /start-celeryworker
# RUN sed -i 's/\r$//g' /start-celeryworker
# RUN chmod +x /start-celeryworker

# COPY ./compose/django/celery/beat/start /start-celerybeat
# RUN sed -i 's/\r$//g' /start-celerybeat
# RUN chmod +x /start-celerybeat


# run entrypoint.sh
# ENTRYPOINT ["/usr/src/app/compose/django/entrypoint.sh"]
