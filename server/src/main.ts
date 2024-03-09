import { serve } from '@hono/node-server';
import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { etag } from 'hono/etag';
import { api_routes } from './api.js';
import { serveStatic } from '@hono/node-server/serve-static';
import { createMiddleware } from 'hono/factory';

const cacheHeaders = createMiddleware(async (c, next) => {
  await next();
  c.res.headers.set('cache-control', 'max-age=604800');
});

const app = new Hono();
app.use('/api/*', cors());
app.use('/*', etag());
app.use('/overlay/*', cacheHeaders);
app.use('/map/*', cacheHeaders);
app.use('/assets/*', cacheHeaders);

const routes = app
  .route('/api', api_routes)
  .use('/*', serveStatic({ root: '../dist' }));

export type AppType = typeof routes;

serve(app, (add) => console.log(`Running on ${add.address}:${add.port}`));
