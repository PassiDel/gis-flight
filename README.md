# Flightradar

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
