# ygwifi

- [Purpose](#Purpose)
- [Examples](#Examples)
- [Getting Started](#Getting_Started)

<br>

## Purpose

Controls managed wifi and AP hotspot separately with a simple API.

- You'll need a wifi [dongle](#Dongles) ([why?](#Dongle)).

Quoting [txwifi](https://github.com/txn2/txwifi) sums this project up:

> This project is intended to aid in developing “configure wifi over wifi” solutions for IOT projects using the Raspberry Pi [Zero W]. The main use case for this project is to reproduce functionality common to devices like Nest or Echo, where the user turns on the device, connects to it and configures it for wifi.

Very similar to [txwifi](https://github.com/txn2/txwifi), but you can safely disable the hotspot without interrupting managed.

Tested on a Raspberry Pi Zero W with [Hypriot](https://blog.hypriot.com/downloads/)

### Dongles

Here's the cheapest I could find:

- [Dongle](https://www.ebay.com/itm/NEW-2018-Mini-USB-WiFi-WLAN-Wireless-Network-Adapter-802-11-Dongle-RTL8188-lapto/143202387869)
- [USB A-to-micro adapter](https://www.amazon.com/gp/product/B015GZOHKW/ref=ppx_yo_dt_b_asin_title_o07_s00?ie=UTF8&psc=1)

Driver for that particular dongle:

- [Driver rtl8188fu](https://github.com/kelebek333/rtl8188fu/tree/arm#how-to-install-for-arm-devices)

Not the most elegant solution, but it works. If you know how to fix the [unexpected behavior](#Dongle) with using the onboard chipset please [open an issue](https://github.com/Ryazbeck/ygwifi/issues/new).

<br>

## Examples

##### Enable hotspot:

```
curl http://localhost:5000/apup
```

##### Disable hotspot:

```
curl http://localhost:5000/apdown
```

##### Scan wifi:

```
curl http://localhost:5000/scan
```

##### Authenticate wifi:

```
curl http://localhost:5000/connect \
   -d '{"ssid":"network", "psk":"password"}' \
   -H "Content-Type: application/json"
```

##### Verify internet connection:

```
curl http://localhost:5000/connected
```

<br>

## Getting Started

1. Clone this repo

   ```
   git clone https://github.com/Ryazbeck/ygwifi.git
   ```

1. Disable host wifi services

   ```
   sudo systemctl mask wpa_supplicant.service
   sudo mv /sbin/wpa_supplicant /sbin/no_wpa_supplicant
   sudo pkill wpa_supplicant
   sudo ifdown --force wlan0
   ```

1. Build and up

   - Development:
     ```
     docker-compose up --build -d
     ```
   - Production:
     ```
     docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
     ```

<br>

#### Dongle

##### Due to unexpected behavior with Pi Zero W onboard wifi chipset when using both the managed wifi and the ap hotspot. Examples:

- ##### The hotspot must be enabled before managed or the hotspot won't come up at all
- ##### The hotspot will drop momentarily when you bring up managed (interrupts captive portal)
- ##### If you want to disable the hotspot after connecting managed you must turn them both down and turn managed up again.
