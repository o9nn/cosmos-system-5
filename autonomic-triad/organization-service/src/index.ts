import express from 'express';
import dotenv from 'dotenv';
import { OrganizationService } from './organization-service';
import { ServiceConfig, createMessage } from '@cosmos/cognitive-core-shared-libraries';

dotenv.config();

const app = express();
app.use(express.json());

const config: ServiceConfig = {
  port: parseInt(process.env.PORT || '3026'),
  serviceName: 'organization-service',
  triadType: 'autonomic',
  serviceType: 'O-4',
  environment: (process.env.NODE_ENV as any) || 'development'
};

const organizationService = new OrganizationService(config);

// Health check endpoint
app.get('/health', (req, res) => {
  res.json(organizationService.getHealth());
});

// Service info endpoint
app.get('/info', (req, res) => {
  res.json({
    serviceName: config.serviceName,
    triad: config.triadType,
    serviceType: config.serviceType,
    dimension: 'Commitment [5-4]',
    position: 'Organization',
    description: 'Background system coordination - Receives Production→Organization flow from Processing (P-5)',
    version: '1.0.0',
    endpoints: [
      'GET /health - Service health check',
      'GET /info - Service information',
      'POST /create - Create system organization',
      'POST /coordinate - Create background coordination',
      'POST /schedule - Schedule maintenance task',
      'POST /execute - Execute maintenance task',
      'GET /status - Get organization status',
      'POST /optimize - Optimize organization',
      'POST /sync - Sync with State Management (S-8)'
    ]
  });
});

// Create system organization
app.post('/create', async (req, res) => {
  try {
    const message = createMessage(
      'CREATE_ORGANIZATION',
      req.body,
      'api-gateway',
      config.serviceName
    );

    const response = await organizationService.process(message);
    res.json(response?.payload || { error: 'No response generated' });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Create background coordination
app.post('/coordinate', async (req, res) => {
  try {
    const message = createMessage(
      'COORDINATE_BACKGROUND',
      req.body,
      'api-gateway',
      config.serviceName
    );

    const response = await organizationService.process(message);
    res.json(response?.payload || { error: 'No response generated' });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Schedule maintenance task
app.post('/schedule', async (req, res) => {
  try {
    const message = createMessage(
      'SCHEDULE_MAINTENANCE',
      req.body,
      'api-gateway',
      config.serviceName
    );

    const response = await organizationService.process(message);
    res.json(response?.payload || { error: 'No response generated' });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Execute maintenance task
app.post('/execute', async (req, res) => {
  try {
    const message = createMessage(
      'EXECUTE_MAINTENANCE',
      req.body,
      'api-gateway',
      config.serviceName
    );

    const response = await organizationService.process(message);
    res.json(response?.payload || { error: 'No response generated' });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get organization status
app.get('/status', async (req, res) => {
  try {
    const message = createMessage(
      'GET_ORGANIZATION_STATUS',
      {
        organizationId: req.query.id,
        includeComponents: req.query.includeComponents === 'true'
      },
      'api-gateway',
      config.serviceName
    );

    const response = await organizationService.process(message);
    res.json(response?.payload || { error: 'No response generated' });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Optimize organization
app.post('/optimize', async (req, res) => {
  try {
    const message = createMessage(
      'OPTIMIZE_ORGANIZATION',
      req.body,
      'api-gateway',
      config.serviceName
    );

    const response = await organizationService.process(message);
    res.json(response?.payload || { error: 'No response generated' });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Sync with State Management service
app.post('/sync', async (req, res) => {
  try {
    const message = createMessage(
      'SYNC_WITH_STATE_MANAGEMENT',
      req.body,
      'api-gateway',
      config.serviceName
    );

    const response = await organizationService.process(message);
    res.json(response?.payload || { error: 'No response generated' });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Initialize and start the service
async function startService() {
  try {
    await organizationService.initialize();

    app.listen(config.port, () => {
      console.log(`Organization Service (O-4) running on port ${config.port}`);
      console.log(`Environment: ${config.environment}`);
      console.log(`Triad: ${config.triadType} | Dimension: Commitment [5-4]`);
      console.log(`Flow: Receives from Processing (P-5), syncs with State Management (S-8)`);
    });
  } catch (error) {
    console.error('Failed to start Organization Service:', error);
    process.exit(1);
  }
}

// Graceful shutdown
process.on('SIGTERM', async () => {
  await organizationService.shutdown();
  process.exit(0);
});

process.on('SIGINT', async () => {
  await organizationService.shutdown();
  process.exit(0);
});

startService();
