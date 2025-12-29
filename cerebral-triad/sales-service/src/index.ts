import express from 'express';
import dotenv from 'dotenv';
import { SalesService } from './sales-service';
import { ServiceConfig, createMessage } from '@cosmos/cognitive-core-shared-libraries';

dotenv.config();

const app = express();
app.use(express.json());

const config: ServiceConfig = {
  port: parseInt(process.env.PORT || '3005'),
  serviceName: 'sales-service',
  triadType: 'cerebral',
  serviceType: 'S-8',
  environment: (process.env.NODE_ENV as any) || 'development'
};

const salesService = new SalesService(config);

// Health check endpoint
app.get('/health', (req, res) => {
  res.json(salesService.getHealth());
});

// Service info endpoint
app.get('/info', (req, res) => {
  res.json({
    serviceName: config.serviceName,
    triad: config.triadType,
    serviceType: config.serviceType,
    dimension: 'Performance [8-1]',
    position: 'Sales',
    description: 'Quality assurance and output promotion - Sales→Market flow',
    version: '1.0.0',
    endpoints: [
      'GET /health - Service health check',
      'GET /info - Service information',
      'POST /assess - Assess output quality',
      'POST /promote - Promote output to channels',
      'POST /readiness - Check market readiness',
      'GET /metrics - Get quality metrics',
      'POST /optimize - Optimize for market'
    ]
  });
});

// Assess output quality
app.post('/assess', async (req, res) => {
  try {
    const message = createMessage(
      'ASSESS_QUALITY',
      req.body,
      'api-gateway',
      config.serviceName
    );

    const response = await salesService.process(message);
    res.json(response?.payload || { error: 'No response generated' });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Promote output to channels
app.post('/promote', async (req, res) => {
  try {
    const message = createMessage(
      'PROMOTE_OUTPUT',
      req.body,
      'api-gateway',
      config.serviceName
    );

    const response = await salesService.process(message);
    res.json(response?.payload || { error: 'No response generated' });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Check market readiness
app.post('/readiness', async (req, res) => {
  try {
    const message = createMessage(
      'CHECK_MARKET_READINESS',
      req.body,
      'api-gateway',
      config.serviceName
    );

    const response = await salesService.process(message);
    res.json(response?.payload || { error: 'No response generated' });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get quality metrics
app.get('/metrics', async (req, res) => {
  try {
    const message = createMessage(
      'GET_QUALITY_METRICS',
      {},
      'api-gateway',
      config.serviceName
    );

    const response = await salesService.process(message);
    res.json(response?.payload || { error: 'No response generated' });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Optimize for market
app.post('/optimize', async (req, res) => {
  try {
    const message = createMessage(
      'OPTIMIZE_FOR_MARKET',
      req.body,
      'api-gateway',
      config.serviceName
    );

    const response = await salesService.process(message);
    res.json(response?.payload || { error: 'No response generated' });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Initialize and start the service
async function startService() {
  try {
    await salesService.initialize();

    app.listen(config.port, () => {
      console.log(`Sales Service (S-8) running on port ${config.port}`);
      console.log(`Environment: ${config.environment}`);
      console.log(`Triad: ${config.triadType} | Dimension: Performance [8-1]`);
    });
  } catch (error) {
    console.error('Failed to start Sales Service:', error);
    process.exit(1);
  }
}

// Graceful shutdown
process.on('SIGTERM', async () => {
  await salesService.shutdown();
  process.exit(0);
});

process.on('SIGINT', async () => {
  await salesService.shutdown();
  process.exit(0);
});

startService();
