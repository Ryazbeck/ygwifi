FROM arm32v6/python:rc-alpine

WORKDIR /

RUN apk update
RUN apk add ifupdown dhclient hostapd wireless-tools wpa_supplicant dnsmasq iw

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY cfg /cfg
COPY src /

ENV FLASK_APP 'app.py'
ENV FLASK_ENV 'development'

CMD flask run