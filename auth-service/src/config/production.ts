type Environment = NodeJS.ProcessEnv;

const hasDatabaseTls = (databaseUrl: string): boolean => {
  try {
    const parsed = new URL(databaseUrl);
    if (!['postgres:', 'postgresql:'].includes(parsed.protocol)) return false;
    const sslMode = parsed.searchParams.get('sslmode')?.toLowerCase();
    const ssl = parsed.searchParams.get('ssl')?.toLowerCase();
    return ['require', 'verify-ca', 'verify-full'].includes(sslMode || '') || ['true', '1', 'require'].includes(ssl || '');
  } catch {
    return false;
  }
};

export const validateProductionConfiguration = (environment: Environment = process.env): void => {
  if (environment.NODE_ENV !== 'production') return;

  const requiredSecrets = ['JWT_SECRET', 'REFRESH_SECRET'];
  for (const name of requiredSecrets) {
    const value = environment[name];
    if (!value || value.length < 32) {
      throw new Error(`${name} must be configured with at least 32 characters in production`);
    }
  }

  if (!environment.DATABASE_URL || !hasDatabaseTls(environment.DATABASE_URL)) {
    throw new Error('A TLS-enabled PostgreSQL DATABASE_URL is required in production');
  }
  if (!environment.FRONTEND_URL?.startsWith('https://')) {
    throw new Error('An HTTPS FRONTEND_URL is required in production');
  }
  if (!environment.REDIS_URL?.startsWith('rediss://')) {
    throw new Error('A TLS-enabled REDIS_URL is required in production');
  }
  if (environment.DATABASE_AUTO_MIGRATE === 'true') {
    throw new Error('DATABASE_AUTO_MIGRATE must be false in production; run npm run migrate first');
  }
};
