FROM arm32v6/python:rc-alpine

WORKDIR /

ARG reqs=$reqs

RUN apk update
RUN apk add wireless-tools iw ifupdown wpa_supplicant hostapd dnsmasq

COPY ${reqs} requirements.txt
RUN pip install -r requirements.txt

COPY cfg /cfg
RUN cp /cfg/interfaces /etc/network

RUN mkdir /etc/udhcpc
RUN echo "RESOLV_CONF=no" > /etc/udhcpc/udhcpc.conf

COPY src /

CMD flask run