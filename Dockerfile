FROM arm32v6/python:rc-alpine

WORKDIR /

RUN apk update
RUN apk add wireless-tools iw ifupdown wpa_supplicant hostapd dnsmasq

#RUN mkdir /etc/network/interfaces.d

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY cfg /cfg
RUN cp /cfg/interfaces /etc/network

RUN mkdir /etc/udhcpc
RUN echo "RESOLV_CONF=no" > /etc/udhcpc/udhcpc.conf

COPY src /

CMD flask run
