import rateLimit from 'express-rate-limit';
import RedisStore from 'rate-limit-redis';
import { redisClient } from '../config/redis.js';

const redisSendCommand = (...args: string[]) => {
  try {
    return redisClient.call(args[0]!, ...args.slice(1)) as any;
  } catch (err) {
    console.error('Rate limiter Redis store error:', err);
    return null;
  }
};

export const loginRateLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // Limit each IP to 5 requests per windowMs
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: 'Too many login attempts from this IP, please try again after 15 minutes' },
  store: new RedisStore({
    sendCommand: redisSendCommand,
  }),
});

export const registerRateLimiter = rateLimit({
  windowMs: 60 * 60 * 1000, // 1 hour
  max: 5, // Limit each IP to 5 registrations per hour
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: 'Too many registration attempts from this IP, please try again after 1 hour' },
  store: new RedisStore({
    sendCommand: redisSendCommand,
  }),
});

export const refreshRateLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 30, // Limit each IP to 30 refresh requests per windowMs
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: 'Too many token refresh requests from this IP, please try again later' },
  store: new RedisStore({
    sendCommand: redisSendCommand,
  }),
});

