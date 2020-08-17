# ygwifi

### IoT WiFi and AP with REST API for Raspberry Pi - Python, Flask, Docker

Intended for Pi configuration via host portal such as a web server or captive portal hosted on a Raspberry Pi.

I've only tested this on a Raspberry Pi Zero W.

Examples:

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

Logging by [Tenable](https://github.com/tenable/flask-logging-demo)