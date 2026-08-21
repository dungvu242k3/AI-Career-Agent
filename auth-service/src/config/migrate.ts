import { pool } from './db.js';
import { migrateAuthDatabase } from './migrations.js';

try {
  const version = await migrateAuthDatabase(pool);
  console.log(`Auth database migrated successfully to schema_version=${version}`);
} finally {
  await pool.end();
}
