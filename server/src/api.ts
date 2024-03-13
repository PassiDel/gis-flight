import { Hono } from 'hono';
import { z } from 'zod';
import { zValidator } from '@hono/zod-validator';
import { fetchFlight, fetchFromRadar } from '@puazzi/flightradar24-client';
import { streamSSE } from 'hono/streaming';
import { Flight, hooks } from './hook.js';
import { influxDB } from './influx.js';

const api = new Hono();

function flightToMinimal(flight: Flight) {
  const { altitude, latitude, longitude, speed, id } = flight;
  return { altitude, latitude, longitude, speed, id };
}

const boundsSchema = z.object({
  west: z.number(),
  east: z.number(),
  north: z.number(),
  south: z.number()
});
export type Trails = {
  flight: string;
  pos: {
    lat: number;
    lon: number;
    speed: number;
    bearing: number;
    altitude: number;
    time: string;
  }[];
}[];

async function fetchTrailsFromDB(data?: z.infer<typeof boundsSchema>) {
  const queryClient = influxDB.getQueryApi('gis');
  let query = `import "experimental/geo"

from(bucket: "data")
    |> range(start: -10m)
    |> geo.shapeData(latField: "latitude", lonField: "longitude", level: 10)`;

  if (data) {
    query = `${query}
    |> geo.filterRows(region: { minLat: ${data.south}, maxLat: ${data.north}, minLon: ${data.west}, maxLon: ${data.east} }, strict: true)`;
  }
  return await queryClient
    .collectRows(query, (values, tableMeta) => {
      const {
        _time,
        altitude,
        bearing,
        callsign,
        destination,
        flight,
        lat,
        lon,
        origin,
        registration,
        speed
      } = tableMeta.toObject(values);
      return {
        _time,
        altitude,
        bearing,
        callsign,
        destination,
        flight,
        lat,
        lon,
        origin,
        registration,
        speed
      };
    })
    .catch(() => [])
    .then((res) =>
      res.reduce((flights, r) => {
        const { flight, lat, lon, altitude, speed, bearing, _time } = r;
        const pos = { lat, lon, altitude, speed, bearing, time: _time };
        const fId = flights.findIndex((f) => f.flight === flight);
        if (fId < 0) {
          flights.push({
            flight,
            pos: [pos]
          });
          return flights;
        }

        flights[fId].pos.push(pos);

        return flights;
      }, [] as Trails)
    );
}

export const api_routes = api
  .post('/flights', zValidator('json', boundsSchema), async (c) => {
    const data = c.req.valid('json');

    const flights = await fetchFromRadar(
      data.north,
      data.west,
      data.south,
      data.east
    );

    return c.json(flights);
  })
  .get('/flight/:id', async (c) => {
    const { id } = c.req.param();

    return c.json(await fetchFlight(id));
  })
  .get(
    '/sse',
    zValidator(
      'query',
      z.object({
        detailed: z.enum(['true', 'false']).optional().default('false')
      })
    ),
    async (c) => {
      const detailed = c.req.valid('query').detailed === 'true';
      return streamSSE(c, async (stream) => {
        let id = 0;
        const messages: Flight[][] = [];
        let keepRunning = true;

        const unregister = hooks.hook('data', async (flights) => {
          messages.push(flights);
        });
        await stream.onAbort(() => {
          unregister();
          keepRunning = false;
        });

        while (keepRunning) {
          if (messages.length > 0) {
            const flights = messages.shift()!!;
            await stream.writeSSE({
              data: JSON.stringify(
                detailed ? flights : flights.map(flightToMinimal)
              ),
              event: 'time-update',
              id: String(id++)
            });
          }
          await stream.sleep(100);
        }
      });
    }
  )
  .post('/trails', zValidator('json', boundsSchema), async (c) => {
    const data = c.req.valid('json');

    const flights = await fetchTrailsFromDB(data);

    return c.json(flights);
  })
  .get('/trails', async (c) => {
    const flights = await fetchTrailsFromDB();

    c.res.headers.set('cache-control', 'max-age=5');
    return c.json(flights);
  });
