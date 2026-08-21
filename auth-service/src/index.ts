import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import cookieParser from 'cookie-parser';
import dotenv from 'dotenv';
import authRoutes from './routes/authRoutes.js';
import { initDb, pool } from './config/db.js';
import { redisClient } from './config/redis.js';
import { validateProductionConfiguration } from './config/production.js';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 4000;

validateProductionConfiguration();

const trustProxyHops = Number.parseInt(process.env.TRUST_PROXY_HOPS || '0', 10);
if (Number.isInteger(trustProxyHops) && trustProxyHops > 0) {
  app.set('trust proxy', trustProxyHops);
}

// Middleware
app.use(helmet());
app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:3000',
  credentials: true,
}));
app.use(express.json({ limit: '32kb' }));
app.use(cookieParser());

// Routes
app.use('/api/v1/auth', authRoutes);

// Health checks
app.get('/health/live', (req, res) => {
  res.status(200).json({ status: 'OK', service: 'Auth Service' });
});

app.get('/health', (req, res) => {
  res.status(200).json({ status: 'OK', service: 'Auth Service' });
});

app.get('/health/ready', async (req, res) => {
  try {
    await Promise.all([pool.query('SELECT 1'), redisClient.ping()]);
    res.status(200).json({ status: 'READY', service: 'Auth Service' });
  } catch {
    res.status(503).json({ status: 'NOT_READY', service: 'Auth Service' });
  }
});

// Start server
const startServer = async () => {
  try {
    await initDb();
    app.listen(PORT, () => {
      console.log(`Auth Service running on port ${PORT}`);
    });
  } catch (error) {
    console.error('Auth Service failed to start:', error);
    process.exit(1);
  }
};

startServer();
