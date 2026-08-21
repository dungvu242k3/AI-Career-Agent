import assert from 'node:assert/strict';
import { test } from 'node:test';

process.env.JWT_SECRET = 'j'.repeat(64);
process.env.REFRESH_SECRET = 'r'.repeat(64);

const {
  generateAccessToken,
  generateRefreshToken,
  verifyRefreshToken,
} = await import('./jwt.js');

test('access token contains the expected issuer, audience, and claims', async () => {
  const token = generateAccessToken(42, 'user@example.com', 'pro');
  const [header, payload] = token.split('.');
  assert.ok(header && payload);
  const claims = JSON.parse(Buffer.from(payload, 'base64url').toString('utf8'));

  assert.equal(JSON.parse(Buffer.from(header, 'base64url').toString('utf8')).alg, 'HS256');
  assert.equal(claims.sub, '42');
  assert.equal(claims.email, 'user@example.com');
  assert.equal(claims.tier, 'pro');
  assert.equal(claims.iss, 'careerpilot-auth');
  assert.equal(claims.aud, 'careerpilot-api');
  assert.ok(claims.exp > claims.iat);
});

test('refresh token round-trips claims and exposes a session id', async () => {
  const generated = generateRefreshToken(7, '00000000-0000-0000-0000-000000000001');
  const claims = verifyRefreshToken(generated.token);

  assert.equal(generated.sessionId, '00000000-0000-0000-0000-000000000001');
  assert.deepEqual(
    { sub: claims?.sub, jti: claims?.jti },
    { sub: '7', jti: '00000000-0000-0000-0000-000000000001' },
  );
});

test('tampered refresh token is rejected', async () => {
  const generated = generateRefreshToken(7, '00000000-0000-0000-0000-000000000002');

  assert.equal(verifyRefreshToken(`${generated.token}tampered`), null);
});
