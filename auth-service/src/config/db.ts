import { Pool } from 'pg';
import dotenv from 'dotenv';
import { AUTH_SCHEMA_VERSION, getAuthSchemaVersion, migrateAuthDatabase } from './migrations.js';

dotenv.config();

export const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

export const initDb = async () => {
  if (process.env.NODE_ENV === 'production') {
    const version = await getAuthSchemaVersion(pool);
    if (version !== AUTH_SCHEMA_VERSION) {
      throw new Error(
        `Auth database schema version ${version} is behind required version ${AUTH_SCHEMA_VERSION}; ` +
        'run npm run migrate before startup',
      );
    }
    console.log(`Auth database schema verified: schema_version=${version}.`);
    return;
  }

  const version = await migrateAuthDatabase(pool);
  console.log(`Database initialized: auth schema_version=${version}.`);
};
