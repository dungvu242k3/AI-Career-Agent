import { Router } from 'express';
import { authController } from '../controllers/authController.js';
import { loginRateLimiter } from '../middleware/rateLimiter.js';

const router = Router();

router.post('/register', authController.register);
router.post('/login', loginRateLimiter, authController.login);
router.post('/refresh', authController.refreshToken);

export default router;
