import jwt from 'jsonwebtoken';
import dotenv from 'dotenv';

dotenv.config();

const JWT_SECRET = process.env.JWT_SECRET || 'super-secret-key-for-dev-only';
const REFRESH_SECRET = process.env.REFRESH_SECRET || 'super-refresh-secret-for-dev-only';

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
