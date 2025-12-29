import express from 'express';
import dotenv from 'dotenv';
import { TreasuryService } from './treasury-service';
import { ServiceConfig, createMessage } from '@cosmos/cognitive-core-shared-libraries';

dotenv.config();

const app = express();
app.use(express.json());

const config: ServiceConfig = {
  port: parseInt(process.env.PORT || '3016'),
  serviceName: 'treasury-service',
  triadType: 'somatic',
  serviceType: 'T-7',
  environment: (process.env.NODE_ENV as any) || 'development'
};

const treasuryService = new TreasuryService(config);

// Health check endpoint
app.get('/health', (req, res) => {
  res.json(treasuryService.getHealth());
});

// Service info endpoint
app.get('/info', (req, res) => {
  res.json({
    serviceName: config.serviceName,
    triad: config.triadType,
    serviceType: config.serviceType,
    dimension: 'Potential [2-7]',
    position: 'Treasury',
    shared: true,
    sharedWith: 'Autonomic Triad (Parasympathetic Polarity)',
    description: 'Motor memory and learned skills storage - Receives Development→Treasury flow',
    version: '1.0.0',
    endpoints: [
      'GET /health - Service health check',
      'GET /info - Service information',
      'POST /store - Store motor memory',
      'POST /retrieve - Retrieve skill by ID/name/type',
      'POST /register - Register learned skill',
      'POST /proficiency - Update skill proficiency',
      'GET /inventory - Get skill inventory',
      'POST /receive - Receive completed skill from Development',
      'POST /integrate - Integrate skill with other services'
    ]
  });
});

// Store motor memory
app.post('/store', async (req, res) => {
  try {
    const message = createMessage(
      'STORE_MOTOR_MEMORY',
      req.body,
      'api-gateway',
      config.serviceName
    );

    const response = await treasuryService.process(message);
    res.json(response?.payload || { error: 'No response generated' });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Retrieve skill
app.post('/retrieve', async (req, res) => {
  try {
    const message = createMessage(
      'RETRIEVE_SKILL',
      req.body,
      'api-gateway',
      config.serviceName
    );

    const response = await treasuryService.process(message);
    res.json(response?.payload || { error: 'No response generated' });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Register learned skill
app.post('/register', async (req, res) => {
  try {
    const message = createMessage(
      'REGISTER_LEARNED_SKILL',
      req.body,
      'api-gateway',
      config.serviceName
    );

    const response = await treasuryService.process(message);
    res.json(response?.payload || { error: 'No response generated' });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Update proficiency
app.post('/proficiency', async (req, res) => {
  try {
    const message = createMessage(
      'UPDATE_PROFICIENCY',
      req.body,
      'api-gateway',
      config.serviceName
    );

    const response = await treasuryService.process(message);
    res.json(response?.payload || { error: 'No response generated' });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get skill inventory
app.get('/inventory', async (req, res) => {
  try {
    const message = createMessage(
      'GET_SKILL_INVENTORY',
      {
        category: req.query.category,
        minProficiency: req.query.minProficiency ? parseFloat(req.query.minProficiency as string) : undefined
      },
      'api-gateway',
      config.serviceName
    );

    const response = await treasuryService.process(message);
    res.json(response?.payload || { error: 'No response generated' });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Receive completed skill from Development service
app.post('/receive', async (req, res) => {
  try {
    const message = createMessage(
      'RECEIVE_FROM_DEVELOPMENT',
      req.body,
      'api-gateway',
      config.serviceName
    );

    const response = await treasuryService.process(message);
    res.json(response?.payload || { error: 'No response generated' });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Integrate skill with other services
app.post('/integrate', async (req, res) => {
  try {
    const message = createMessage(
      'INTEGRATE_SKILL',
      req.body,
      'api-gateway',
      config.serviceName
    );

    const response = await treasuryService.process(message);
    res.json(response?.payload || { error: 'No response generated' });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Initialize and start the service
async function startService() {
  try {
    await treasuryService.initialize();

    app.listen(config.port, () => {
      console.log(`Treasury Service (T-7) running on port ${config.port}`);
      console.log(`Environment: ${config.environment}`);
      console.log(`Triad: ${config.triadType} | Dimension: Potential [2-7]`);
      console.log(`Shared Parasympathetic: Receives from Development Service (PD-2)`);
    });
  } catch (error) {
    console.error('Failed to start Treasury Service:', error);
    process.exit(1);
  }
}

// Graceful shutdown
process.on('SIGTERM', async () => {
  await treasuryService.shutdown();
  process.exit(0);
});

process.on('SIGINT', async () => {
  await treasuryService.shutdown();
  process.exit(0);
});

startService();
