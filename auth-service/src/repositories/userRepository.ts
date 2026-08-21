import { pool } from '../config/db.js';
import { createHash } from 'crypto';

export interface User {
  id: number;
  email: string;
  password_hash: string;
  tier: string;
  created_at: Date;
}

export class UserRepository {
  async findById(id: number): Promise<User | null> {
    const result = await pool.query('SELECT * FROM users WHERE id = $1', [id]);
    return result.rows[0] || null;
  }

  async findByEmail(email: string): Promise<User | null> {
    const result = await pool.query('SELECT * FROM users WHERE email = $1', [email]);
    return result.rows[0] || null;
  }

  async create(email: string, passwordHash: string): Promise<User> {
    const result = await pool.query(
      'INSERT INTO users (email, password_hash) VALUES ($1, $2) RETURNING id, email, tier, created_at',
      [email, passwordHash]
    );
    return result.rows[0];
  }

  async createRefreshSession(sessionId: string, userId: number, token: string, expiresAt: Date): Promise<void> {
    await pool.query(
      `INSERT INTO refresh_sessions (id, user_id, token_hash, expires_at)
       VALUES ($1, $2, $3, $4)`,
      [sessionId, userId, hashToken(token), expiresAt],
    );
  }

  async rotateRefreshSession(
    previousSessionId: string,
    userId: number,
    previousToken: string,
    nextSessionId: string,
    nextToken: string,
    nextExpiresAt: Date,
  ): Promise<boolean> {
    const client = await pool.connect();
    try {
      await client.query('BEGIN');
      const consumed = await client.query(
        `UPDATE refresh_sessions
         SET revoked_at = CURRENT_TIMESTAMP
         WHERE id = $1 AND user_id = $2 AND token_hash = $3
           AND revoked_at IS NULL AND expires_at > CURRENT_TIMESTAMP
         RETURNING id`,
        [previousSessionId, userId, hashToken(previousToken)],
      );
      if (consumed.rowCount !== 1) {
        await client.query('ROLLBACK');
        return false;
      }
      await client.query(
        `INSERT INTO refresh_sessions (id, user_id, token_hash, expires_at)
         VALUES ($1, $2, $3, $4)`,
        [nextSessionId, userId, hashToken(nextToken), nextExpiresAt],
      );
      await client.query('COMMIT');
      return true;
    } catch (error) {
      await client.query('ROLLBACK');
      throw error;
    } finally {
      client.release();
    }
  }

  async revokeRefreshSession(sessionId: string, userId: number, token: string): Promise<void> {
    await pool.query(
      `UPDATE refresh_sessions SET revoked_at = CURRENT_TIMESTAMP
       WHERE id = $1 AND user_id = $2 AND token_hash = $3 AND revoked_at IS NULL`,
      [sessionId, userId, hashToken(token)],
    );
  }
}

const hashToken = (token: string): string => createHash('sha256').update(token).digest('hex');

export const userRepository = new UserRepository();
