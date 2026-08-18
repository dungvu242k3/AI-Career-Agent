import { Router } from 'express';
import { authController } from '../controllers/authController.js';
import { loginRateLimiter, registerRateLimiter, refreshRateLimiter } from '../middleware/rateLimiter.js';

const router = Router();

router.post('/register', registerRateLimiter, authController.register);
router.post('/login', loginRateLimiter, authController.login);
router.post('/refresh', refreshRateLimiter, authController.refreshToken);
router.post('/logout', authController.logout);

export default router;

