FROM python:3.8

# RUN  apt-get update && apt-get install -y  binutils libproj-dev gdal-bin libgdal-dev


ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip3 install -r requirements.txt
COPY src /code/