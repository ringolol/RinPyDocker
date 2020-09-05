FROM python:3.8.3-alpine

WORKDIR /code

COPY . .

RUN apk update
RUN apk add --upgrade gnuplot

COPY ./requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt