import rateLimit from 'express-rate-limit';
import RedisStore from 'rate-limit-redis';
import { redisClient } from '../config/redis.js';

export const loginRateLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // Limit each IP to 5 requests per windowMs
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: 'Too many login attempts from this IP, please try again after 15 minutes' },
  store: new RedisStore({
    sendCommand: (...args: string[]) => redisClient.call(args[0]!, ...args.slice(1)) as any,
  }),
});
