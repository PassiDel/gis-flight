# Flightradar

## Requirements
The system is designed to run on a Raspberry 4 with debian linux installed. A ESP32 chip needs to be connected via serial USB interface. It needs the `hardware/serial_neopixel_command` installed on it. 

Other requirements are:
- python 3.10
- node.js 18
- npm 10


## Getting started

Download the `EPSG3857 Tiles` from [OpenFlightMaps](https://www.openflightmaps.org/ed-germany/?airac=2311&language=local), unzip and copy the `/clip/aero/512/latest` folder to `./public/overlay`.

It should look something like this:

```txt
/public/overlay
├── 4
│   └── 8
│       └── 5.png
├── 5
│   ├── 16
│   │   ├── 10.png
│   │   └── 11.png
│   └── 17
│       ├── 10.png
│       └── 11.png
├── 6
...
```

### Start the frontend

```shell
npm install
npm run dev
```

### Start the backend

```shell
cd server
npm install
npm run dev
```

### To set up the environment on a Raspberry Pi

1. git clone this repository
2. transmit the overlay tiles via ftp

```shell
sudo apt-get update
sudo apt-get update
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
pip install Shapely, Rtree
sudo apt-get install -y libopenblas-base
sudo apt-get install -y libspatialindex-dev
```
