import express from 'express';
import dotenv from 'dotenv';
import { MarketService } from './market-service';
import { ServiceConfig, createMessage } from '@cosmos/cognitive-core-shared-libraries';

dotenv.config();

const app = express();
app.use(express.json());

const config: ServiceConfig = {
  port: parseInt(process.env.PORT || '3006'),
  serviceName: 'market-service',
  triadType: 'cerebral',
  serviceType: 'M-1',
  environment: (process.env.NODE_ENV as any) || 'development'
};

const marketService = new MarketService(config);

// Health check endpoint
app.get('/health', (req, res) => {
  res.json(marketService.getHealth());
});

// Service info endpoint
app.get('/info', (req, res) => {
  res.json({
    serviceName: config.serviceName,
    triad: config.triadType,
    serviceType: config.serviceType,
    dimension: 'Performance [8-1]',
    position: 'Market',
    description: 'Market presentation and external interface - Receives Sales→Market flow',
    version: '1.0.0',
    endpoints: [
      'GET /health - Service health check',
      'GET /info - Service information',
      'POST /analyze - Analyze market segment',
      'GET /interfaces - Get interface status',
      'POST /register - Register external interface',
      'POST /feedback - Process performance feedback',
      'GET /intelligence - Get market intelligence',
      'POST /optimize - Optimize for potential (feeds back to PD-2)'
    ]
  });
});

// Analyze market segment
app.post('/analyze', async (req, res) => {
  try {
    const message = createMessage(
      'ANALYZE_MARKET',
      req.body,
      'api-gateway',
      config.serviceName
    );

    const response = await marketService.process(message);
    res.json(response?.payload || { error: 'No response generated' });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get interface status
app.get('/interfaces', async (req, res) => {
  try {
    const message = createMessage(
      'INTERFACE_STATUS',
      { interfaceId: req.query.id },
      'api-gateway',
      config.serviceName
    );

    const response = await marketService.process(message);
    res.json(response?.payload || { error: 'No response generated' });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Register external interface
app.post('/register', async (req, res) => {
  try {
    const message = createMessage(
      'REGISTER_INTERFACE',
      req.body,
      'api-gateway',
      config.serviceName
    );

    const response = await marketService.process(message);
    res.json(response?.payload || { error: 'No response generated' });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Process performance feedback
app.post('/feedback', async (req, res) => {
  try {
    const message = createMessage(
      'PROCESS_FEEDBACK',
      req.body,
      'api-gateway',
      config.serviceName
    );

    const response = await marketService.process(message);
    res.json(response?.payload || { error: 'No response generated' });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get market intelligence
app.get('/intelligence', async (req, res) => {
  try {
    const message = createMessage(
      'GET_MARKET_INTELLIGENCE',
      {
        domain: req.query.domain,
        timeframe: req.query.timeframe
      },
      'api-gateway',
      config.serviceName
    );

    const response = await marketService.process(message);
    res.json(response?.payload || { error: 'No response generated' });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Optimize for potential (feedback to Processing Director)
app.post('/optimize', async (req, res) => {
  try {
    const message = createMessage(
      'OPTIMIZE_POTENTIAL',
      req.body,
      'api-gateway',
      config.serviceName
    );

    const response = await marketService.process(message);
    res.json(response?.payload || { error: 'No response generated' });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Initialize and start the service
async function startService() {
  try {
    await marketService.initialize();

    app.listen(config.port, () => {
      console.log(`Market Service (M-1) running on port ${config.port}`);
      console.log(`Environment: ${config.environment}`);
      console.log(`Triad: ${config.triadType} | Dimension: Performance [8-1]`);
      console.log(`Flow: Receives from Sales Service, feeds back to Processing Director`);
    });
  } catch (error) {
    console.error('Failed to start Market Service:', error);
    process.exit(1);
  }
}

// Graceful shutdown
process.on('SIGTERM', async () => {
  await marketService.shutdown();
  process.exit(0);
});

process.on('SIGINT', async () => {
  await marketService.shutdown();
  process.exit(0);
});

startService();
