import { Redis } from 'ioredis';
import dotenv from 'dotenv';

dotenv.config();

const REDIS_URL = process.env.REDIS_URL || 'redis://localhost:6379/0';

export const redisClient = new Redis(REDIS_URL, {
  maxRetriesPerRequest: null,
  enableReadyCheck: false,
});

redisClient.on('error', (err: any) => {
  console.error('Redis connection error:', err);
});

redisClient.on('connect', () => {
  console.log('Connected to Redis for Rate Limiting');
});
