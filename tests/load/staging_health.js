import http from 'k6/http';
import { check, sleep } from 'k6';

const backendUrl = (__ENV.BACKEND_URL || '').replace(/\/$/, '');
if (!backendUrl) {
  throw new Error('BACKEND_URL is required, for example https://api.staging.example');
}

const virtualUsers = Number(__ENV.K6_VUS || 5);
const duration = __ENV.K6_DURATION || '30s';
const maxP95Milliseconds = Number(__ENV.K6_MAX_P95_MS || 500);
const maxErrorRate = Number(__ENV.K6_MAX_ERROR_RATE || 0.01);
const sleepSeconds = Number(__ENV.K6_SLEEP_SECONDS || 0.2);

export const options = {
  scenarios: {
    staging_health: {
      executor: 'constant-vus',
      vus: virtualUsers,
      duration,
      gracefulStop: '10s',
    },
  },
  thresholds: {
    http_req_failed: [`rate<${maxErrorRate}`],
    http_req_duration: [`p(95)<${maxP95Milliseconds}`],
    checks: ['rate>0.99'],
  },
};

function traceId(response) {
  return response.headers['X-Trace-ID'] || response.headers['X-Trace-Id'];
}

export function setup() {
  const ready = http.get(`${backendUrl}/health/ready`, { tags: { name: 'health_ready' } });
  if (ready.status !== 200) {
    throw new Error(`Backend readiness failed before load test: HTTP ${ready.status}`);
  }
}

export default function () {
  const requestId = `k6-${__VU}-${__ITER}`;
  const response = http.get(`${backendUrl}/health/live`, {
    headers: { 'X-Request-ID': requestId },
    tags: { name: 'health_live' },
  });

  check(response, {
    'liveness is 200': (result) => result.status === 200,
    'request has a trace ID': (result) => Boolean(traceId(result)),
  });
  sleep(sleepSeconds);
}
