import { createHooks } from 'hookable';
import { fetchFromRadar } from '@puazzi/flightradar24-client';
import { influxDB } from './influx.js';
import { Point } from '@influxdata/influxdb-client';

export type Flight = Awaited<ReturnType<typeof fetchFromRadar>>[0];
export const hooks = createHooks<{
  data: (flights: Flight[]) => void;
}>();

const west = 6.45;
const east = 11.18;
const south = 51.1;
const north = 55.05;
setInterval(async () => {
  const flights = await fetchFromRadar(north, west, south, east);
  await hooks.callHook('data', flights);
  console.log('data', flights.length);
}, 5_000);

if (process.arch === 'x64') {
  hooks.hook('data', async (flights) => {
    const writeClient = influxDB.getWriteApi('gis', 'data');

    const points = flights.map((f) => {
      return new Point('flight')
        .tag('flight', f.id)
        .tag('callsign', f.callsign || '')
        .tag('origin', f.origin || '')
        .tag('destination', f.destination || '')
        .tag('registration', f.registration || '')
        .timestamp(new Date((f.timestamp || 0) * 1000))
        .floatField('latitude', f.latitude)
        .floatField('longitude', f.longitude)
        .floatField('altitude', f.altitude)
        .floatField('bearing', f.bearing)
        .floatField('speed', f.speed);
    });

    writeClient.writePoints(points);
    await writeClient.flush();
    await writeClient.close();
  });
}
