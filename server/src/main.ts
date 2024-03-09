import { serve } from '@hono/node-server';
import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { api_routes } from './api.js';
import { serveStatic } from '@hono/node-server/serve-static';

const app = new Hono();
app.use('/api/*', cors());

const routes = app
  .route('/api', api_routes)
  .use('/*', serveStatic({ root: '../dist' }));

export type AppType = typeof routes;

serve(app, (add) => console.log(`Running on ${add.address}:${add.port}`));
