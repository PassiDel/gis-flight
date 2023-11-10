import { Hono } from 'hono';
import { z } from 'zod';
import { zValidator } from '@hono/zod-validator';
import { fetchFromRadar, fetchFlight } from 'flightradar24-client';

const api = new Hono();

export const api_routes = api.post(
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
    // console.log(JSON.stringify(flights));

    return c.jsonT(flights);
  }
);

api.get('/flight/:id', async (c) => {
  const { id } = c.req.param();
  console.log(id, await fetchFlight(id));

  return c.jsonT({
    success: true
  });
});
