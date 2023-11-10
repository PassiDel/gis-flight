import { serve } from '@hono/node-server';
import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { api_routes } from './api';

const app = new Hono();
app.use('/api/*', cors());

const routes = app
  .get('/', (c) => c.text('Hello Node.js!'))
  .route('/api', api_routes);

export type AppType = typeof routes;

serve(app, (add) => console.log(`Running on ${add.address}:${add.port}`));
