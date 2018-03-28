# sabobpel
Sabinas Bobbahn vom 19.3.2018


Benötigt:
* 20m Drainage-Rohr
* 1 x Start-Vorrichtung
* 1 x Katapult
* lots of jello shots
* 5 Bobs

* 1 x Arduino (bluno)
* 3 x lichtschranke von Baumer (oder so)
* 2 x Buzzer
* 1 x overpowered LED mit heatsink
* 1 x Laptop mit externem Monitor
* 3 x TX1 mit Kamera Stream


## Laptop Stream Receiver
```
gstd &
```
Dann Python Skript starten..

## TX1 Kamera Stream
(change host=.. IP at the end to that of the Laptop)
```
gst-launch-1.0 nvcamerasrc ! 'video/x-raw(memory:NVMM), width=1280, height=720' ! nvvidconv flip-method=2 ! omxh264enc bitrate=5000000 ! 'video/x-h264, stream-format=(string)byte-stream' ! h264parse ! mpegtsmux ! rtpmp2tpay ! udpsink port=5000 async=false sync=false host=192.168.0.105
```

## Fotos
https://drive.switch.ch/index.php/s/CItPrnC5HTCkyij?path=%2F
