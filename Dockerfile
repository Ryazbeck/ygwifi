FROM arm32v6/alpine:latest

WORKDIR /

RUN apk update
RUN apk add dhclient bridge hostapd wireless-tools wpa_supplicant dnsmasq iw

COPY requirements.txt requirements.txt
RUN pip3 install -i requirements.txt

RUN mkdir -p /etc/wpa_supplicant/
RUN mkdir -p /etc/hostapd/

COPY cfg/hostapd.conf /etc/hostapd/hostapd.conf
COPY cfg/dnsmasq.conf /etc/dnsmasq.conf
COPY cfg/sysctl.conf /etc/sysctl.conf

VOLUME /var/log/ /var/log/
RUN mkdir -p /var/log/yarden-gnome

ENV FLASK_APP app
ENV FLASK_ENV development

CMD flask run
