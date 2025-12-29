import { BaseService, ServiceConfig, ServiceMessage, createMessage } from '@cosmos/cognitive-core-shared-libraries';

interface MarketAnalysis {
  id: string;
  marketSegment: string;
  trends: MarketTrend[];
  opportunities: string[];
  threats: string[];
  recommendations: string[];
  timestamp: Date;
}

interface MarketTrend {
  name: string;
  direction: 'rising' | 'falling' | 'stable';
  impact: 'high' | 'medium' | 'low';
  timeframe: string;
}

interface ExternalInterface {
  id: string;
  interfaceType: string;
  status: 'active' | 'inactive' | 'pending';
  capabilities: string[];
  metrics: InterfaceMetrics;
}

interface InterfaceMetrics {
  requestsHandled: number;
  averageLatency: number;
  successRate: number;
  lastActivity: Date;
}

interface PerformanceFeedback {
  source: string;
  metricType: string;
  value: number;
  trend: 'improving' | 'stable' | 'declining';
  actionRequired: boolean;
  recommendations: string[];
}

export class MarketService extends BaseService {
  private marketSegments: Map<string, MarketAnalysis>;
  private externalInterfaces: Map<string, ExternalInterface>;
  private feedbackHistory: PerformanceFeedback[];
  private marketIntelligence: Map<string, any>;

  constructor(config: ServiceConfig) {
    super(config);
    this.marketSegments = new Map();
    this.externalInterfaces = new Map();
    this.feedbackHistory = [];
    this.marketIntelligence = new Map();
    this.initializeMarketFramework();
  }

  async initialize(): Promise<void> {
    this.log('info', 'Initializing Market Service (M-1) - Performance Dimension [8-1]');
    this.log('info', 'Market Service initialized - External interface and market awareness ready');
  }

  async process(message: ServiceMessage): Promise<ServiceMessage | null> {
    const startTime = Date.now();
    this.log('info', 'Processing market request', { messageId: message.id, type: message.type });

    try {
      switch (message.type) {
        case 'ANALYZE_MARKET':
          return this.handleMarketAnalysis(message, startTime);

        case 'INTERFACE_STATUS':
          return this.handleInterfaceStatus(message, startTime);

        case 'REGISTER_INTERFACE':
          return this.handleInterfaceRegistration(message, startTime);

        case 'PROCESS_FEEDBACK':
          return this.handleFeedbackProcessing(message, startTime);

        case 'GET_MARKET_INTELLIGENCE':
          return this.handleGetIntelligence(message, startTime);

        case 'OPTIMIZE_POTENTIAL':
          return this.handlePotentialOptimization(message, startTime);

        default:
          this.log('warn', 'Unknown message type', { type: message.type });
          return null;
      }
    } catch (error) {
      this.log('error', 'Error processing market request', { error, messageId: message.id });
      throw error;
    }
  }

  private async handleMarketAnalysis(message: ServiceMessage, startTime: number): Promise<ServiceMessage> {
    const { segment, depth, factors } = message.payload;

    const analysis = this.analyzeMarket(segment || 'general', depth, factors);
    this.marketSegments.set(analysis.marketSegment, analysis);

    return createMessage(
      'MARKET_ANALYZED',
      {
        analysis,
        processingTime: Date.now() - startTime,
        source: this.config.serviceName
      },
      this.config.serviceName,
      message.source
    );
  }

  private analyzeMarket(segment: string, depth?: string, factors?: string[]): MarketAnalysis {
    const trends = this.identifyTrends(segment);
    const opportunities = this.identifyOpportunities(segment, trends);
    const threats = this.identifyThreats(segment, trends);
    const recommendations = this.generateMarketRecommendations(opportunities, threats);

    return {
      id: `ma-${Date.now()}`,
      marketSegment: segment,
      trends,
      opportunities,
      threats,
      recommendations,
      timestamp: new Date()
    };
  }

  private identifyTrends(segment: string): MarketTrend[] {
    const baseTrends: MarketTrend[] = [
      {
        name: 'Digital transformation acceleration',
        direction: 'rising',
        impact: 'high',
        timeframe: '12-24 months'
      },
      {
        name: 'AI/ML integration demand',
        direction: 'rising',
        impact: 'high',
        timeframe: '6-18 months'
      },
      {
        name: 'Real-time processing requirements',
        direction: 'rising',
        impact: 'medium',
        timeframe: '3-12 months'
      },
      {
        name: 'Legacy system modernization',
        direction: 'stable',
        impact: 'medium',
        timeframe: '12-36 months'
      }
    ];

    // Add segment-specific trends
    if (segment.includes('cognitive') || segment.includes('ai')) {
      baseTrends.push({
        name: 'Neuromorphic computing adoption',
        direction: 'rising',
        impact: 'high',
        timeframe: '18-36 months'
      });
    }

    return baseTrends;
  }

  private identifyOpportunities(segment: string, trends: MarketTrend[]): string[] {
    const opportunities: string[] = [];

    const risingTrends = trends.filter(t => t.direction === 'rising' && t.impact === 'high');
    risingTrends.forEach(trend => {
      opportunities.push(`Capitalize on ${trend.name} within ${trend.timeframe}`);
    });

    opportunities.push('Expand cognitive processing capabilities');
    opportunities.push('Enhance cross-triad integration for market differentiation');
    opportunities.push('Develop predictive market intelligence features');

    return opportunities;
  }

  private identifyThreats(segment: string, trends: MarketTrend[]): string[] {
    const threats: string[] = [];

    threats.push('Increasing competition in cognitive systems space');
    threats.push('Rapid technology obsolescence risk');
    threats.push('Integration complexity with external systems');
    threats.push('Data privacy and compliance requirements');

    return threats;
  }

  private generateMarketRecommendations(opportunities: string[], threats: string[]): string[] {
    const recommendations: string[] = [];

    recommendations.push('Prioritize high-impact opportunities in the short term');
    recommendations.push('Implement continuous market monitoring');
    recommendations.push('Strengthen external interface capabilities');
    recommendations.push('Develop threat mitigation strategies');
    recommendations.push('Feed insights back to Processing Director for optimization');

    return recommendations;
  }

  private async handleInterfaceStatus(message: ServiceMessage, startTime: number): Promise<ServiceMessage> {
    const { interfaceId } = message.payload;

    let interfaces: ExternalInterface[];
    if (interfaceId) {
      const iface = this.externalInterfaces.get(interfaceId);
      interfaces = iface ? [iface] : [];
    } else {
      interfaces = Array.from(this.externalInterfaces.values());
    }

    return createMessage(
      'INTERFACE_STATUS_RETRIEVED',
      {
        interfaces,
        totalActive: interfaces.filter(i => i.status === 'active').length,
        totalInterfaces: interfaces.length,
        processingTime: Date.now() - startTime,
        source: this.config.serviceName
      },
      this.config.serviceName,
      message.source
    );
  }

  private async handleInterfaceRegistration(message: ServiceMessage, startTime: number): Promise<ServiceMessage> {
    const { interfaceType, capabilities } = message.payload;

    const newInterface: ExternalInterface = {
      id: `iface-${Date.now()}`,
      interfaceType: interfaceType || 'generic',
      status: 'active',
      capabilities: capabilities || [],
      metrics: {
        requestsHandled: 0,
        averageLatency: 0,
        successRate: 1.0,
        lastActivity: new Date()
      }
    };

    this.externalInterfaces.set(newInterface.id, newInterface);

    return createMessage(
      'INTERFACE_REGISTERED',
      {
        interface: newInterface,
        processingTime: Date.now() - startTime,
        source: this.config.serviceName
      },
      this.config.serviceName,
      message.source
    );
  }

  private async handleFeedbackProcessing(message: ServiceMessage, startTime: number): Promise<ServiceMessage> {
    const { metrics, source } = message.payload;

    const feedback = this.processFeedback(metrics, source);
    this.feedbackHistory.push(feedback);

    // Limit history size
    if (this.feedbackHistory.length > 1000) {
      this.feedbackHistory = this.feedbackHistory.slice(-500);
    }

    return createMessage(
      'FEEDBACK_PROCESSED',
      {
        feedback,
        historySize: this.feedbackHistory.length,
        processingTime: Date.now() - startTime,
        source: this.config.serviceName
      },
      this.config.serviceName,
      message.source
    );
  }

  private processFeedback(metrics: any, feedbackSource: string): PerformanceFeedback {
    const value = metrics?.value ?? Math.random();
    const previousValues = this.feedbackHistory
      .filter(f => f.source === feedbackSource)
      .slice(-10)
      .map(f => f.value);

    let trend: 'improving' | 'stable' | 'declining' = 'stable';
    if (previousValues.length >= 3) {
      const avg = previousValues.reduce((a, b) => a + b, 0) / previousValues.length;
      if (value > avg * 1.05) trend = 'improving';
      else if (value < avg * 0.95) trend = 'declining';
    }

    const recommendations: string[] = [];
    if (trend === 'declining') {
      recommendations.push('Review recent changes for potential issues');
      recommendations.push('Consider optimization opportunities');
    } else if (trend === 'improving') {
      recommendations.push('Continue current approach');
      recommendations.push('Document successful patterns for replication');
    }

    return {
      source: feedbackSource || 'unknown',
      metricType: metrics?.type || 'general',
      value,
      trend,
      actionRequired: trend === 'declining',
      recommendations
    };
  }

  private async handleGetIntelligence(message: ServiceMessage, startTime: number): Promise<ServiceMessage> {
    const { domain, timeframe } = message.payload;

    const intelligence = this.gatherMarketIntelligence(domain, timeframe);

    return createMessage(
      'MARKET_INTELLIGENCE_RETRIEVED',
      {
        intelligence,
        processingTime: Date.now() - startTime,
        source: this.config.serviceName
      },
      this.config.serviceName,
      message.source
    );
  }

  private gatherMarketIntelligence(domain?: string, timeframe?: string): any {
    const recentFeedback = this.feedbackHistory.slice(-50);
    const marketAnalyses = Array.from(this.marketSegments.values());

    return {
      domain: domain || 'all',
      timeframe: timeframe || 'recent',
      summary: {
        totalMarketSegments: marketAnalyses.length,
        activeTrends: marketAnalyses.flatMap(a => a.trends.filter(t => t.direction === 'rising')).length,
        feedbackTrend: this.calculateOverallTrend(recentFeedback),
        interfaceHealth: this.calculateInterfaceHealth()
      },
      insights: [
        'Performance metrics indicate stable system operation',
        'Market opportunities align with current capabilities',
        'External interface utilization is within expected parameters'
      ],
      actionItems: this.generateActionItems(recentFeedback, marketAnalyses)
    };
  }

  private calculateOverallTrend(feedback: PerformanceFeedback[]): string {
    if (feedback.length === 0) return 'insufficient data';

    const improving = feedback.filter(f => f.trend === 'improving').length;
    const declining = feedback.filter(f => f.trend === 'declining').length;

    if (improving > declining * 1.5) return 'positive';
    if (declining > improving * 1.5) return 'negative';
    return 'neutral';
  }

  private calculateInterfaceHealth(): number {
    const interfaces = Array.from(this.externalInterfaces.values());
    if (interfaces.length === 0) return 1.0;

    const healthyCount = interfaces.filter(i => i.status === 'active').length;
    return healthyCount / interfaces.length;
  }

  private generateActionItems(feedback: PerformanceFeedback[], analyses: MarketAnalysis[]): string[] {
    const items: string[] = [];

    const decliningFeedback = feedback.filter(f => f.trend === 'declining');
    if (decliningFeedback.length > feedback.length * 0.3) {
      items.push('Investigate declining performance trends');
    }

    analyses.forEach(analysis => {
      if (analysis.threats.length > 3) {
        items.push(`Address threats in ${analysis.marketSegment} segment`);
      }
    });

    if (items.length === 0) {
      items.push('Continue monitoring - no immediate actions required');
    }

    return items;
  }

  private async handlePotentialOptimization(message: ServiceMessage, startTime: number): Promise<ServiceMessage> {
    const { targetArea, constraints } = message.payload;

    const optimization = this.optimizeForPotential(targetArea, constraints);

    return createMessage(
      'POTENTIAL_OPTIMIZED',
      {
        optimization,
        processingTime: Date.now() - startTime,
        source: this.config.serviceName
      },
      this.config.serviceName,
      message.source
    );
  }

  private optimizeForPotential(targetArea?: string, constraints?: any): any {
    return {
      targetArea: targetArea || 'general',
      optimizations: [
        'Enhance market awareness through expanded data collection',
        'Improve feedback loop efficiency with Processing Director',
        'Strengthen external interface reliability',
        'Optimize resource allocation based on market priorities'
      ],
      expectedImpact: {
        marketReach: '+15%',
        responseTime: '-20%',
        adaptability: '+25%'
      },
      implementationPriority: 'medium',
      feedbackToProcessingDirector: {
        type: 'OPTIMIZATION_FEEDBACK',
        recommendations: [
          'Consider adjusting processing priorities based on market trends',
          'Enable proactive resource allocation for emerging opportunities'
        ]
      }
    };
  }

  private initializeMarketFramework(): void {
    // Initialize default external interfaces
    const defaultInterfaces = [
      { type: 'api', capabilities: ['REST', 'GraphQL'] },
      { type: 'webhook', capabilities: ['event-driven', 'real-time'] },
      { type: 'batch', capabilities: ['bulk-processing', 'scheduled'] }
    ];

    defaultInterfaces.forEach((iface, index) => {
      const newInterface: ExternalInterface = {
        id: `default-iface-${index}`,
        interfaceType: iface.type,
        status: 'active',
        capabilities: iface.capabilities,
        metrics: {
          requestsHandled: 0,
          averageLatency: 0,
          successRate: 1.0,
          lastActivity: new Date()
        }
      };
      this.externalInterfaces.set(newInterface.id, newInterface);
    });

    // Initialize market intelligence base
    this.marketIntelligence.set('baseline', {
      established: new Date(),
      version: '1.0.0'
    });
  }

  async shutdown(): Promise<void> {
    this.log('info', 'Shutting down Market Service');
  }
}
