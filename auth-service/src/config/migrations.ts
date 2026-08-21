import type { Pool } from 'pg';

export const AUTH_SCHEMA_VERSION = 1;

const migrations = [
  {
    version: 1,
    name: 'auth_baseline_schema',
    sql: `
      CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        tier VARCHAR(50) DEFAULT 'free',
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
      );
      CREATE TABLE IF NOT EXISTS refresh_sessions (
        id UUID PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        token_hash CHAR(64) NOT NULL,
        expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
        revoked_at TIMESTAMP WITH TIME ZONE,
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
      );
      CREATE INDEX IF NOT EXISTS idx_refresh_sessions_active
        ON refresh_sessions(user_id, expires_at) WHERE revoked_at IS NULL;
    `,
  },
] as const;

const migrationTableSql = `
  CREATE TABLE IF NOT EXISTS auth_schema_migrations (
    version INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    applied_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
  )
`;

export async function getAuthSchemaVersion(pool: Pool): Promise<number> {
  const tableResult = await pool.query<{ table_name: string | null }>(
    "SELECT to_regclass('public.auth_schema_migrations')::text AS table_name",
  );
  if (!tableResult.rows[0]?.table_name) return 0;

  const result = await pool.query<{ version: number }>(
    `SELECT COALESCE(MAX(version), 0)::int AS version
     FROM auth_schema_migrations`,
  );
  return result.rows[0]?.version ?? 0;
}

export async function migrateAuthDatabase(pool: Pool): Promise<number> {
  const client = await pool.connect();
  try {
    await client.query('BEGIN');
    await client.query("SELECT pg_advisory_xact_lock(hashtext('careerpilot:auth-schema'))");
    await client.query(migrationTableSql);

    const appliedResult = await client.query<{ version: number }>(
      'SELECT version FROM auth_schema_migrations ORDER BY version',
    );
    const applied = new Set(appliedResult.rows.map((row) => Number(row.version)));
    const unknown = [...applied].filter(
      (version) => !migrations.some((migration) => migration.version === version),
    );
    if (unknown.length > 0) {
      throw new Error(`Auth database schema is newer than this application: ${unknown.join(', ')}`);
    }

    for (const migration of migrations) {
      if (applied.has(migration.version)) continue;
      await client.query(migration.sql);
      await client.query(
        'INSERT INTO auth_schema_migrations(version, name) VALUES($1, $2)',
        [migration.version, migration.name],
      );
    }

    await client.query('COMMIT');
    return AUTH_SCHEMA_VERSION;
  } catch (error) {
    await client.query('ROLLBACK');
    throw error;
  } finally {
    client.release();
  }
}
