FROM python:3.8.3-alpine

RUN mkdir /code
WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev

COPY ./requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

RUN adduser restricted_user -D
RUN cp -R ./default_user_files/* /home/restricted_user
RUN chmod 777 -R /home/restricted_user
RUN apk update
RUN apk add --upgrade gnuplot
