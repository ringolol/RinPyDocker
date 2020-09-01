FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
RUN useradd -m restricted_user
RUN cp -R ./default_user_files/* /home/restricted_user
RUN chmod 777 -R /home/restricted_user
RUN apt update
RUN apt install gnuplot -y
