FROM ubuntu:18.04

MAINTAINER Farhan "surel.farhan@gmail.com"

RUN apt-get update && apt-get install -y \
    python3 python3-pip \
    fonts-liberation libappindicator3-1 libasound2 libatk-bridge2.0-0 \
    libnspr4 libnss3 lsb-release xdg-utils libxss1 libdbus-glib-1-2 \
    curl unzip wget \
    xvfb chromium-browser

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN wget -O /usr/lib/chromium-browser/chromedriver.zip https://chromedriver.storage.googleapis.com/75.0.3770.140/chromedriver_linux64.zip

RUN unzip /usr/lib/chromium-browser/chromedriver.zip

RUN pip3 install -r requirements.txt

COPY . /app

ENTRYPOINT [ "python3" ]

CMD [ "app.py" ]