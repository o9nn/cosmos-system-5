import express from 'express';
import dotenv from 'dotenv';
import { DevelopmentService } from './development-service';
import { ServiceConfig, createMessage } from '@cosmos/cognitive-core-shared-libraries';

dotenv.config();

const app = express();
app.use(express.json());

const config: ServiceConfig = {
  port: parseInt(process.env.PORT || '3015'),
  serviceName: 'development-service',
  triadType: 'somatic',
  serviceType: 'PD-2',
  environment: (process.env.NODE_ENV as any) || 'development'
};

const developmentService = new DevelopmentService(config);

// Health check endpoint
app.get('/health', (req, res) => {
  res.json(developmentService.getHealth());
});

// Service info endpoint
app.get('/info', (req, res) => {
  res.json({
    serviceName: config.serviceName,
    triad: config.triadType,
    serviceType: config.serviceType,
    dimension: 'Potential [2-7]',
    position: 'Development',
    shared: true,
    sharedWith: 'Autonomic Triad (Parasympathetic Polarity)',
    description: 'Motor development coordination - Development→Treasury flow',
    version: '1.0.0',
    endpoints: [
      'GET /health - Service health check',
      'GET /info - Service information',
      'POST /plan - Create motor development plan',
      'POST /optimize - Optimize behavioral patterns',
      'POST /allocate - Allocate resources',
      'POST /coordinate - Parasympathetic coordination with Autonomic',
      'GET /status - Get development status',
      'POST /progress - Update skill progress'
    ]
  });
});

// Create development plan
app.post('/plan', async (req, res) => {
  try {
    const message = createMessage(
      'CREATE_DEVELOPMENT_PLAN',
      req.body,
      'api-gateway',
      config.serviceName
    );

    const response = await developmentService.process(message);
    res.json(response?.payload || { error: 'No response generated' });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Optimize behavioral patterns
app.post('/optimize', async (req, res) => {
  try {
    const message = createMessage(
      'OPTIMIZE_BEHAVIOR',
      req.body,
      'api-gateway',
      config.serviceName
    );

    const response = await developmentService.process(message);
    res.json(response?.payload || { error: 'No response generated' });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Allocate resources
app.post('/allocate', async (req, res) => {
  try {
    const message = createMessage(
      'ALLOCATE_RESOURCES',
      req.body,
      'api-gateway',
      config.serviceName
    );

    const response = await developmentService.process(message);
    res.json(response?.payload || { error: 'No response generated' });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Parasympathetic coordination with Autonomic triad
app.post('/coordinate', async (req, res) => {
  try {
    const message = createMessage(
      'COORDINATE_PARASYMPATHETIC',
      req.body,
      'api-gateway',
      config.serviceName
    );

    const response = await developmentService.process(message);
    res.json(response?.payload || { error: 'No response generated' });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get development status
app.get('/status', async (req, res) => {
  try {
    const message = createMessage(
      'GET_DEVELOPMENT_STATUS',
      { planId: req.query.planId },
      'api-gateway',
      config.serviceName
    );

    const response = await developmentService.process(message);
    res.json(response?.payload || { error: 'No response generated' });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Update skill progress
app.post('/progress', async (req, res) => {
  try {
    const message = createMessage(
      'UPDATE_SKILL_PROGRESS',
      req.body,
      'api-gateway',
      config.serviceName
    );

    const response = await developmentService.process(message);
    res.json(response?.payload || { error: 'No response generated' });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Initialize and start the service
async function startService() {
  try {
    await developmentService.initialize();

    app.listen(config.port, () => {
      console.log(`Development Service (PD-2) running on port ${config.port}`);
      console.log(`Environment: ${config.environment}`);
      console.log(`Triad: ${config.triadType} | Dimension: Potential [2-7]`);
      console.log(`Shared Parasympathetic: Coordinates with Autonomic Process Director`);
    });
  } catch (error) {
    console.error('Failed to start Development Service:', error);
    process.exit(1);
  }
}

// Graceful shutdown
process.on('SIGTERM', async () => {
  await developmentService.shutdown();
  process.exit(0);
});

process.on('SIGINT', async () => {
  await developmentService.shutdown();
  process.exit(0);
});

startService();
