import assert from 'node:assert/strict';
import test from 'node:test';
import { validateProductionConfiguration } from './production.js';

const validProductionEnvironment = {
  NODE_ENV: 'production',
  JWT_SECRET: 'a'.repeat(32),
  REFRESH_SECRET: 'b'.repeat(32),
  DATABASE_URL: 'postgresql://careerpilot:password@db.example/careerpilot?sslmode=require',
  FRONTEND_URL: 'https://app.example',
  REDIS_URL: 'rediss://redis.example:6380/0',
  DATABASE_AUTO_MIGRATE: 'false',
};

test('accepts a complete production configuration with TLS dependencies', () => {
  assert.doesNotThrow(() => validateProductionConfiguration(validProductionEnvironment));
});

test('rejects a plaintext PostgreSQL connection in production', () => {
  assert.throws(
    () => validateProductionConfiguration({ ...validProductionEnvironment, DATABASE_URL: 'postgresql://db.example/careerpilot' }),
    /TLS-enabled PostgreSQL/,
  );
});

test('rejects plaintext Redis in production', () => {
  assert.throws(
    () => validateProductionConfiguration({ ...validProductionEnvironment, REDIS_URL: 'redis://redis.example:6379/0' }),
    /TLS-enabled REDIS_URL/,
  );
});
