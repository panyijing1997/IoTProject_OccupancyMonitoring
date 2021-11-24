FROM python:3
WORKDIR /myApp
RUN apt-get install gcc
RUN pip3 install --upgrade pip
RUN pip3 install flask
RUN pip3 install Flask-MQTT
RUN pip3 install numpy
RUN pip3 install DateTime

COPY . .


EXPOSE 80
CMD [ "python3","-u", "app.py"]