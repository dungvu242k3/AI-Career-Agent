import type { Request, Response } from 'express';
import { authService } from '../services/authService.js';
import { z } from 'zod';
import { verifyRefreshToken, generateAccessToken } from '../utils/jwt.js';

const registerSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8).regex(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/, 
    "Password must contain at least one uppercase letter, one lowercase letter, one number and one special character"),
});

const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(1),
});

export class AuthController {
  async register(req: Request, res: Response) {
    try {
      const { email, password } = registerSchema.parse(req.body);
      const result = await authService.register(email, password);
      res.status(201).json({ message: 'User registered successfully', user: result.user });
    } catch (error: any) {
      if (error instanceof z.ZodError) {
        res.status(400).json({ error: 'Validation failed', details: error.issues });
      } else if (error.message === 'Email already registered') {
        res.status(409).json({ error: error.message });
      } else {
        res.status(500).json({ error: 'Internal server error' });
      }
    }
  }

  async login(req: Request, res: Response) {
    try {
      const { email, password } = loginSchema.parse(req.body);
      const result = await authService.login(email, password);
      
      // Set HttpOnly Cookie for Refresh Token
      res.cookie('refreshToken', result.refreshToken, {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'strict',
        maxAge: 7 * 24 * 60 * 60 * 1000 // 7 days
      });

      res.status(200).json({ 
        message: 'Login successful',
        accessToken: result.accessToken, 
        user: result.user 
      });
    } catch (error: any) {
      if (error instanceof z.ZodError) {
        res.status(400).json({ error: 'Validation failed', details: error.issues });
      } else if (error.message === 'Invalid email or password') {
        res.status(401).json({ error: error.message });
      } else {
        res.status(500).json({ error: 'Internal server error' });
      }
    }
  }

  async refreshToken(req: Request, res: Response) {
    try {
      const token = req.cookies?.refreshToken;
      if (!token) {
        return res.status(401).json({ error: 'No refresh token provided' });
      }

      const decoded = verifyRefreshToken(token);
      if (!decoded) {
        return res.status(401).json({ error: 'Invalid or expired refresh token' });
      }

      // Check if user still exists
      const user = await authService.findById(decoded.sub);
      if (!user) {
        return res.status(401).json({ error: 'User no longer exists' });
      }

      const accessToken = generateAccessToken(user.id, user.email, user.tier || 'free');
      
      res.status(200).json({ accessToken });
    } catch (error) {
      res.status(500).json({ error: 'Internal server error' });
    }
  }
}

export const authController = new AuthController();
