FROM python:3.8.3-alpine

WORKDIR /code/

COPY ./*.py ./
COPY ./default_user_files ./default_user_files

RUN apk update
RUN apk add --upgrade gnuplot

COPY ./requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# compile python into .pyc and remove .py
RUN python -m compileall . -b
RUN rm *.py