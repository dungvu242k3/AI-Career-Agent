import { userRepository } from '../repositories/userRepository.js';
import { hashPassword, verifyPassword } from '../utils/password.js';
import { generateAccessToken, generateRefreshToken } from '../utils/jwt.js';

export class AuthService {
  async register(email: string, passwordRaw: string) {
    const hashed = await hashPassword(passwordRaw);
    try {
      const user = await userRepository.create(email, hashed);
      return {
        user: {
          id: user.id,
          email: user.email,
          tier: user.tier,
        }
      };
    } catch (error: any) {
      if (error.code === '23505') {
        throw new Error('Email already registered');
      }
      throw error;
    }
  }

  async findById(id: number) {
    return await userRepository.findById(id);
  }

  async login(email: string, passwordRaw: string) {
    const user = await userRepository.findByEmail(email);
    if (!user) {
      throw new Error('Invalid email or password');
    }

    const isValid = await verifyPassword(passwordRaw, user.password_hash);
    if (!isValid) {
      throw new Error('Invalid email or password');
    }

    const accessToken = generateAccessToken(user.id, user.email, user.tier);
    const refreshToken = generateRefreshToken(user.id);

    return {
      accessToken,
      refreshToken,
      user: {
        id: user.id,
        email: user.email,
        tier: user.tier,
      }
    };
  }
}

export const authService = new AuthService();
