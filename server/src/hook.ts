import { createHooks } from 'hookable';
import { fetchFromRadar } from 'flightradar24-client';

export type Flight = Awaited<ReturnType<typeof fetchFromRadar>>[0];
export const hooks = createHooks<{
  data: (flights: Flight[]) => void;
}>();

setInterval(async () => {
  // TODO: add correct coordinates
  const flights = await fetchFromRadar(55, 7, 48, 9);
  await hooks.callHook('data', flights);
  console.log('data', flights.length);
  // TODO: set timer
}, 5_000);

// TODO: add influx
// hooks.hook('data', async (flights) => {
//   // influx create point...
// })
