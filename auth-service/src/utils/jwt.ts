import jwt from 'jsonwebtoken';
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

export const generateAccessToken = (userId: number, email: string, tier: string): string => {
  return jwt.sign({ sub: userId, email, tier }, getJwtSecret(), { expiresIn: '15m' });
};

export const generateRefreshToken = (userId: number): string => {
  return jwt.sign({ sub: userId }, getRefreshSecret(), { expiresIn: '7d' });
};

export const verifyRefreshToken = (token: string): any => {
  try {
    return jwt.verify(token, getRefreshSecret(), { algorithms: ['HS256'] });
  } catch (error) {
    return null;
  }
};

