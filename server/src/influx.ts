import { InfluxDB } from '@influxdata/influxdb-client';

export const influxDB = new InfluxDB({
  url: 'http://127.0.0.1:8006',
  timeout: 10_000,
  token: 'rootroot'
});
