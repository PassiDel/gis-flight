import { Hono } from 'hono';
import { z } from 'zod';
import { zValidator } from '@hono/zod-validator';
import { fetchFlight, fetchFromRadar } from 'flightradar24-client';
import { streamSSE } from 'hono/streaming';
import { Flight, hooks } from './hook.js';

const api = new Hono();

function flightToMinimal(flight: Flight) {
  const { altitude, latitude, longitude, speed, id } = flight;
  return { altitude, latitude, longitude, speed, id };
}

export const api_routes = api
  .post(
    '/flights',
    zValidator(
      'json',
      z.object({
        west: z.number(),
        east: z.number(),
        north: z.number(),
        south: z.number()
      })
    ),
    async (c) => {
      const data = c.req.valid('json');

      const flights = await fetchFromRadar(
        data.north,
        data.west,
        data.south,
        data.east
      );

      return c.json(flights);
    }
  )
  .get('/flight/:id', async (c) => {
    const { id } = c.req.param();
    console.log(id, await fetchFlight(id));

    return c.json({
      success: true
    });
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
          console.log(id, flights.length);
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
  );
