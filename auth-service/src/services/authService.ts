import { userRepository } from '../repositories/userRepository.js';
import { hashPassword, verifyPassword } from '../utils/password.js';
import { generateAccessToken, generateRefreshToken, verifyRefreshToken } from '../utils/jwt.js';

const REFRESH_TOKEN_TTL_MS = 7 * 24 * 60 * 60 * 1000;
let dummyPasswordHash: Promise<string> | undefined;

const normalizeEmail = (email: string): string => email.trim().toLowerCase();

const equalizeUnknownUserTiming = async (password: string): Promise<void> => {
  dummyPasswordHash ??= hashPassword('careerpilot-timing-only-password');
  await verifyPassword(password, await dummyPasswordHash);
};

export class AuthService {
  async register(email: string, passwordRaw: string) {
    const normalizedEmail = normalizeEmail(email);
    const hashed = await hashPassword(passwordRaw);
    try {
      const user = await userRepository.create(normalizedEmail, hashed);
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
    const user = await userRepository.findByEmail(normalizeEmail(email));
    if (!user) {
      await equalizeUnknownUserTiming(passwordRaw);
      throw new Error('Invalid email or password');
    }

    const isValid = await verifyPassword(passwordRaw, user.password_hash);
    if (!isValid) {
      throw new Error('Invalid email or password');
    }

    const accessToken = generateAccessToken(user.id, user.email, user.tier);
    const refresh = generateRefreshToken(user.id);
    await userRepository.createRefreshSession(
      refresh.sessionId,
      user.id,
      refresh.token,
      new Date(Date.now() + REFRESH_TOKEN_TTL_MS),
    );

    return {
      accessToken,
      refreshToken: refresh.token,
      user: {
        id: user.id,
        email: user.email,
        tier: user.tier,
      }
    };
  }

  async refresh(refreshToken: string) {
    const claims = verifyRefreshToken(refreshToken);
    const userId = Number(claims?.sub);
    if (!claims || !Number.isSafeInteger(userId) || userId <= 0 || !claims.jti) {
      throw new Error('Invalid refresh token');
    }

    const user = await userRepository.findById(userId);
    if (!user) {
      throw new Error('Invalid refresh token');
    }

    const next = generateRefreshToken(user.id);
    const rotated = await userRepository.rotateRefreshSession(
      claims.jti,
      user.id,
      refreshToken,
      next.sessionId,
      next.token,
      new Date(Date.now() + REFRESH_TOKEN_TTL_MS),
    );
    if (!rotated) {
      throw new Error('Invalid refresh token');
    }
    return {
      accessToken: generateAccessToken(user.id, user.email, user.tier),
      refreshToken: next.token,
    };
  }

  async logout(refreshToken: string | undefined): Promise<void> {
    if (!refreshToken) return;
    const claims = verifyRefreshToken(refreshToken);
    const userId = Number(claims?.sub);
    if (claims?.jti && Number.isSafeInteger(userId) && userId > 0) {
      await userRepository.revokeRefreshSession(claims.jti, userId, refreshToken);
    }
  }
}

export const authService = new AuthService();
