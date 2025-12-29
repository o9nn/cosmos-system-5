import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import { createProxyMiddleware } from 'http-proxy-middleware';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

// Security and CORS middleware
app.use(helmet());
app.use(cors());
app.use(express.json());

// Service discovery configuration - Complete 18-Service [[D-T]-[P-O]-[S-M]] Architecture
// System 5: C-S-A [3-6-9] Potential-Commitment-Performance Topology
const services: Record<string, Record<string, { url: string; path: string; serviceType: string; dimension: string; shared?: boolean }>> = {
  'cerebral': {
    // Potential Dimension [2-7]: Development → Treasury
    'thought-service': { url: 'http://thought-service:3001', path: '/cerebral/thoughts', serviceType: 'T-7', dimension: '[2-7]' },
    'processing-director': { url: 'http://processing-director:3002', path: '/cerebral/processing', serviceType: 'PD-2', dimension: '[2-7]' },
    // Commitment Dimension [5-4]: Production → Organization
    'processing-service': { url: 'http://cerebral-processing:3003', path: '/cerebral/process', serviceType: 'P-5', dimension: '[5-4]' },
    'output-service': { url: 'http://cerebral-output:3004', path: '/cerebral/output', serviceType: 'O-4', dimension: '[5-4]' },
    // Performance Dimension [8-1]: Sales → Market
    'sales-service': { url: 'http://cerebral-sales:3005', path: '/cerebral/sales', serviceType: 'S-8', dimension: '[8-1]' },
    'market-service': { url: 'http://cerebral-market:3006', path: '/cerebral/market', serviceType: 'M-1', dimension: '[8-1]' }
  },
  'somatic': {
    // Potential Dimension [2-7]: Development → Treasury (Shared Parasympathetic)
    'development-service': { url: 'http://somatic-development:3015', path: '/somatic/development', serviceType: 'PD-2', dimension: '[2-7]', shared: true },
    'treasury-service': { url: 'http://somatic-treasury:3016', path: '/somatic/treasury', serviceType: 'T-7', dimension: '[2-7]', shared: true },
    // Commitment Dimension [5-4]: Production → Organization
    'processing-service': { url: 'http://somatic-processing:3013', path: '/somatic/process', serviceType: 'P-5', dimension: '[5-4]' },
    'output-service': { url: 'http://somatic-output:3014', path: '/somatic/output', serviceType: 'O-4', dimension: '[5-4]' },
    // Performance Dimension [8-1]: Sales → Market
    'sensory-service': { url: 'http://sensory:3012', path: '/somatic/sensory', serviceType: 'S-8', dimension: '[8-1]' },
    'motor-control-service': { url: 'http://motor-control:3011', path: '/somatic/motor', serviceType: 'M-1', dimension: '[8-1]' }
  },
  'autonomic': {
    // Potential Dimension [2-7]: Development → Treasury
    'process-director': { url: 'http://autonomic-director:3023', path: '/autonomic/director', serviceType: 'PD-2', dimension: '[2-7]' },
    'trigger-service': { url: 'http://trigger:3025', path: '/autonomic/trigger', serviceType: 'T-7', dimension: '[2-7]' },
    // Commitment Dimension [5-4]: Production → Organization
    'processing-service': { url: 'http://autonomic-processing:3024', path: '/autonomic/process', serviceType: 'P-5', dimension: '[5-4]' },
    'organization-service': { url: 'http://autonomic-organization:3026', path: '/autonomic/organization', serviceType: 'O-4', dimension: '[5-4]' },
    // Performance Dimension [8-1]: Sales → Market
    'state-management': { url: 'http://state-management:3022', path: '/autonomic/state', serviceType: 'S-8', dimension: '[8-1]' },
    'monitoring-service': { url: 'http://monitoring:3021', path: '/autonomic/monitoring', serviceType: 'M-1', dimension: '[8-1]' }
  }
};

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    version: '1.0.0',
    services: Object.keys(services).length,
    uptime: process.uptime()
  });
});

// API Documentation endpoint
app.get('/api/docs', (req, res) => {
  const routes = [];

  for (const [triad, triadServices] of Object.entries(services)) {
    for (const [serviceName, config] of Object.entries(triadServices)) {
      routes.push({
        triad,
        service: serviceName,
        serviceType: config.serviceType,
        dimension: config.dimension,
        path: config.path,
        shared: config.shared || false,
        description: `${serviceName} (${config.serviceType}) - ${config.dimension} in ${triad} triad`
      });
    }
  }

  // Calculate service distribution
  const dimensionCounts = { '[2-7]': 0, '[5-4]': 0, '[8-1]': 0 };
  routes.forEach(r => dimensionCounts[r.dimension as keyof typeof dimensionCounts]++);

  res.json({
    title: 'Cognitive Cities API Gateway - System 5',
    version: '2.0.0',
    description: 'Complete 18-Service [[D-T]-[P-O]-[S-M]] Neurological Architecture',
    architecture: {
      topology: 'C-S-A [3-6-9] Potential-Commitment-Performance',
      totalServices: routes.length,
      dimensionalFlows: {
        '[2-7] Development→Treasury': dimensionCounts['[2-7]'],
        '[5-4] Production→Organization': dimensionCounts['[5-4]'],
        '[8-1] Sales→Market': dimensionCounts['[8-1]']
      },
      parasympatheticSharing: 'Somatic & Autonomic share [2-7] dimension services'
    },
    routes
  });
});

// Dynamic proxy setup for services
for (const [triad, triadServices] of Object.entries(services)) {
  for (const [serviceName, config] of Object.entries(triadServices)) {
    app.use(config.path, createProxyMiddleware({
      target: config.url,
      changeOrigin: true,
      pathRewrite: {
        [`^${config.path}`]: ''
      },
      onError: (err, req, res) => {
        console.error(`Proxy error for ${serviceName}:`, err.message);
        res.status(503).json({
          error: 'Service unavailable',
          service: serviceName,
          triad: triad
        });
      },
      onProxyReq: (proxyReq, req, res) => {
        console.log(`Routing ${req.method} ${req.path} to ${serviceName}`);
      }
    }));
  }
}

// Catch-all route for undefined endpoints
app.use('*', (req, res) => {
  res.status(404).json({
    error: 'Endpoint not found',
    message: 'This endpoint does not exist in the Cognitive Cities API',
    availableRoutes: '/api/docs'
  });
});

// Error handling middleware
app.use((err: Error, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error('Gateway error:', err);
  res.status(500).json({
    error: 'Internal gateway error',
    message: err.message
  });
});

// Start the server
app.listen(PORT, () => {
  console.log(`🌐 Cognitive Cities API Gateway running on port ${PORT}`);
  console.log(`📚 API Documentation available at http://localhost:${PORT}/api/docs`);
  console.log(`🔍 Health check available at http://localhost:${PORT}/health`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('Shutting down API Gateway...');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('Shutting down API Gateway...');
  process.exit(0);
});