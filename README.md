<!-- Space: <space key> -->


# ygwifi

- [Purpose](#Purpose)
- [Why do I need a dongle?](#Why-do-I-need-a-dongle?)
- [Examples](#Examples)
- [Run ygwifi](#Run-ygwifi)

<br>

## Purpose

Controls managed wifi and AP hotspot separately with a simple API.

- You'll need a wifi [dongle](#Why-do-I-need-a-dongle?).

Quoting [txwifi](https://github.com/txn2/txwifi) sums this project up:

> This project is intended to aid in developing “configure wifi over wifi” solutions for IOT projects using the Raspberry Pi [Zero W]. The main use case for this project is to reproduce functionality common to devices like Nest or Echo, where the user turns on the device, connects to it and configures it for wifi.

Very similar to [txwifi](https://github.com/txn2/txwifi), but you can safely disable the hotspot without interrupting managed.

Tested on a Raspberry Pi Zero W with [Hypriot](https://blog.hypriot.com/downloads/)

<br>

## Why do I need a dongle?

Due to unexpected behavior with Pi Zero W onboard wifi chipset when using both the managed wifi and the ap hotspot. Examples:

- The hotspot must be enabled before managed or the hotspot won't come up at all
- The hotspot will drop momentarily when you bring up managed (interrupts captive portal)
- If you want to disable the hotspot after connecting managed you must turn them both down and turn managed up again.

Not the most elegant solution, but it works. If you know how to fix the unexpected behavior with the onboard chipset please [open an issue](https://github.com/Ryazbeck/ygwifi/issues/new)

It seems that to control dongles from inside a Docker container the drivers must be installed with [dkms](https://wiki.archlinux.org/index.php/Dynamic_Kernel_Module_Support). I'm not sure why, but if you do please share.

You can find cheap dongles on Ebay and they may require some searching for the driver.

Here's some wifi dongle drivers:

- [rtl8188fu](https://github.com/kelebek333/rtl8188fu/tree/arm#how-to-install-for-arm-devices)
- [rtl8812au](https://github.com/gnab/rtl8812au) (go down to DKMS in README)
- [rtl8188eus](https://github.com/aircrack-ng/rtl8188eus) (run the included [dkms-install.sh](https://github.com/aircrack-ng/rtl8188eus/blob/v5.3.9/dkms-install.sh))
- [rtl8723au](https://github.com/lwfinger/rtl8723au/blob/master/README.dkms)

If drivers need a Makefile in `/usr/src/<kernel-ver>/arch/armv6l` [you can link it to the arm folder](https://github.com/lwfinger/rtl8723au/issues/62#issuecomment-373945831)

You'll need to convert USB to micro if you're using a Zero, here's a few sources:

- [Amazon](https://www.amazon.com/gp/product/B015GZOHKW/ref=ppx_yo_dt_b_asin_title_o07_s00?ie=UTF8&psc=1)
- [Adafruit](https://www.adafruit.com/product/2910)
- [Digikey](https://www.digikey.com/product-detail/en/sparkfun-electronics/COM-14567/1568-1821-ND/8324538)

Or you can use this, which is great for development:

- [4-Port Stackable USB Hub HAT for Raspberry Pi Zero W](https://www.amazon.com/gp/product/B01K9IVUYM/ref=ppx_yo_dt_b_asin_title_o02_s00?ie=UTF8&psc=1)

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

## Run ygwifi

Interacting with either wifi chip from the host machine could interfere with the functionality of ygwifi.

For best results disable host wifi:

```
sudo systemctl mask wpa_supplicant.service
sudo mv /sbin/wpa_supplicant /sbin/no_wpa_supplicant
sudo pkill wpa_supplicant
sudo ifdown --force wlan0 wlan1
```

Run ygwifi:

```
docker run -d --name ygwifi ryazbeck/ygwifi:latest
```
