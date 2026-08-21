import jwt from 'jsonwebtoken';
import { randomUUID } from 'crypto';
import dotenv from 'dotenv';

dotenv.config();

const getJwtSecret = (): string => {
  const secret = process.env.JWT_SECRET;
  if (!secret) {
    throw new Error('JWT_SECRET environment variable is missing. Please define it in your .env file.');
  }
  return secret;
};

const getRefreshSecret = (): string => {
  const secret = process.env.REFRESH_SECRET;
  if (!secret) {
    throw new Error('REFRESH_SECRET environment variable is missing. Please define it in your .env file.');
  }
  return secret;
};

const issuer = process.env.JWT_ISSUER || 'careerpilot-auth';
const audience = process.env.JWT_AUDIENCE || 'careerpilot-api';

export const generateAccessToken = (userId: number, email: string, tier: string): string => {
  return jwt.sign({ sub: String(userId), email, tier }, getJwtSecret(), {
    algorithm: 'HS256',
    expiresIn: '15m',
    issuer,
    audience,
  });
};

export const generateRefreshToken = (userId: number, sessionId = randomUUID()): { token: string; sessionId: string } => {
  const token = jwt.sign({ sub: String(userId), jti: sessionId }, getRefreshSecret(), {
    algorithm: 'HS256',
    expiresIn: '7d',
    issuer,
    audience,
  });
  return { token, sessionId };
};

export interface RefreshTokenClaims {
  sub: string;
  jti: string;
  exp: number;
}

export const verifyRefreshToken = (token: string): RefreshTokenClaims | null => {
  try {
    return jwt.verify(token, getRefreshSecret(), { algorithms: ['HS256'], issuer, audience }) as RefreshTokenClaims;
  } catch (error) {
    return null;
  }
};
