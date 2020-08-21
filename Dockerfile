FROM arm32v6/python:rc-alpine

WORKDIR /

RUN apk update
RUN apk add ifupdown dhclient hostapd wireless-tools wpa_supplicant dnsmasq iw

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

RUN mkdir -p /etc/wpa_supplicant/
RUN mkdir -p /etc/hostapd/

COPY cfg/hostapd.conf /cfg/hostapd.conf
COPY cfg/dnsmasq.conf /cfg/dnsmasq.conf
COPY cfg/wpa_supplicant.conf /cfg/wpa_supplicant.conf
COPY cfg/interfaces /etc/network/

COPY app /app

ENV FLASK_APP 'app'
ENV FLASK_ENV 'development'

CMD flask run