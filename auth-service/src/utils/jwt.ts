import jwt from 'jsonwebtoken';
import dotenv from 'dotenv';

dotenv.config();

const isProduction = process.env.NODE_ENV === 'production';
const JWT_SECRET = process.env.JWT_SECRET || (isProduction ? (() => { throw new Error('JWT_SECRET must be defined in production'); })() : 'super-secret-key-for-dev-only');
const REFRESH_SECRET = process.env.REFRESH_SECRET || (isProduction ? (() => { throw new Error('REFRESH_SECRET must be defined in production'); })() : 'super-refresh-secret-for-dev-only');


export const generateAccessToken = (userId: number, email: string, tier: string): string => {
  return jwt.sign({ sub: userId, email, tier }, JWT_SECRET, { expiresIn: '15m' });
};

export const generateRefreshToken = (userId: number): string => {
  return jwt.sign({ sub: userId }, REFRESH_SECRET, { expiresIn: '7d' });
};

export const verifyRefreshToken = (token: string): any => {
  try {
    return jwt.verify(token, REFRESH_SECRET, { algorithms: ['HS256'] });
  } catch (error) {
    return null;
  }
};
