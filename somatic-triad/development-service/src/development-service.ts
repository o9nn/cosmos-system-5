import { BaseService, ServiceConfig, ServiceMessage, createMessage } from '@cosmos/cognitive-core-shared-libraries';

interface MotorDevelopmentPlan {
  id: string;
  skillTarget: string;
  currentLevel: number;
  targetLevel: number;
  stages: DevelopmentStage[];
  timeline: string;
  resources: string[];
  status: 'planning' | 'active' | 'completed' | 'paused';
}

interface DevelopmentStage {
  id: string;
  name: string;
  objectives: string[];
  duration: string;
  prerequisites: string[];
  completionCriteria: string[];
  progress: number;
}

interface BehavioralOptimization {
  id: string;
  targetBehavior: string;
  currentEfficiency: number;
  optimizations: OptimizationAction[];
  expectedImprovement: number;
  parasympatheticCoordination: boolean;
}

interface OptimizationAction {
  action: string;
  priority: 'high' | 'medium' | 'low';
  effort: number;
  impact: number;
}

interface ResourceAllocation {
  id: string;
  resourceType: string;
  allocated: number;
  available: number;
  utilization: number;
  targets: string[];
}

export class DevelopmentService extends BaseService {
  private developmentPlans: Map<string, MotorDevelopmentPlan>;
  private optimizationHistory: BehavioralOptimization[];
  private resourceAllocations: Map<string, ResourceAllocation>;
  private sharedParasympatheticState: Map<string, any>;

  constructor(config: ServiceConfig) {
    super(config);
    this.developmentPlans = new Map();
    this.optimizationHistory = [];
    this.resourceAllocations = new Map();
    this.sharedParasympatheticState = new Map();
    this.initializeDevelopmentFramework();
  }

  async initialize(): Promise<void> {
    this.log('info', 'Initializing Development Service (PD-2) - Potential Dimension [2-7]');
    this.log('info', 'Shared Parasympathetic Polarity: Coordinating with Autonomic Triad');
    this.log('info', 'Development Service initialized - Motor development coordination ready');
  }

  async process(message: ServiceMessage): Promise<ServiceMessage | null> {
    const startTime = Date.now();
    this.log('info', 'Processing development request', { messageId: message.id, type: message.type });

    try {
      switch (message.type) {
        case 'CREATE_DEVELOPMENT_PLAN':
          return this.handleCreateDevelopmentPlan(message, startTime);

        case 'OPTIMIZE_BEHAVIOR':
          return this.handleBehaviorOptimization(message, startTime);

        case 'ALLOCATE_RESOURCES':
          return this.handleResourceAllocation(message, startTime);

        case 'COORDINATE_PARASYMPATHETIC':
          return this.handleParasympatheticCoordination(message, startTime);

        case 'GET_DEVELOPMENT_STATUS':
          return this.handleGetDevelopmentStatus(message, startTime);

        case 'UPDATE_SKILL_PROGRESS':
          return this.handleUpdateSkillProgress(message, startTime);

        default:
          this.log('warn', 'Unknown message type', { type: message.type });
          return null;
      }
    } catch (error) {
      this.log('error', 'Error processing development request', { error, messageId: message.id });
      throw error;
    }
  }

  private async handleCreateDevelopmentPlan(message: ServiceMessage, startTime: number): Promise<ServiceMessage> {
    const { skillTarget, currentLevel, targetLevel, timeline } = message.payload;

    const plan = this.createDevelopmentPlan(skillTarget, currentLevel, targetLevel, timeline);
    this.developmentPlans.set(plan.id, plan);

    return createMessage(
      'DEVELOPMENT_PLAN_CREATED',
      {
        plan,
        processingTime: Date.now() - startTime,
        source: this.config.serviceName
      },
      this.config.serviceName,
      message.source
    );
  }

  private createDevelopmentPlan(
    skillTarget: string,
    currentLevel: number = 0,
    targetLevel: number = 1,
    timeline?: string
  ): MotorDevelopmentPlan {
    const levelGap = targetLevel - currentLevel;
    const stageCount = Math.max(3, Math.ceil(levelGap * 5));

    const stages: DevelopmentStage[] = [];
    for (let i = 0; i < stageCount; i++) {
      stages.push({
        id: `stage-${i + 1}`,
        name: `Development Stage ${i + 1}`,
        objectives: this.generateStageObjectives(skillTarget, i, stageCount),
        duration: `${Math.ceil(7 / stageCount)} days`,
        prerequisites: i > 0 ? [`stage-${i}`] : [],
        completionCriteria: [`Achieve ${Math.round(((i + 1) / stageCount) * 100)}% proficiency`],
        progress: 0
      });
    }

    return {
      id: `plan-${Date.now()}`,
      skillTarget: skillTarget || 'motor-skill',
      currentLevel,
      targetLevel,
      stages,
      timeline: timeline || '30 days',
      resources: this.identifyRequiredResources(skillTarget),
      status: 'planning'
    };
  }

  private generateStageObjectives(skillTarget: string, stageIndex: number, totalStages: number): string[] {
    const progressPercent = Math.round(((stageIndex + 1) / totalStages) * 100);

    const baseObjectives = [
      `Master foundational elements (${progressPercent}% target)`,
      `Integrate with existing motor patterns`,
      `Validate through behavioral output`
    ];

    if (stageIndex === 0) {
      baseObjectives.unshift('Establish baseline motor patterns');
    } else if (stageIndex === totalStages - 1) {
      baseObjectives.push('Achieve full integration with Treasury (T-7)');
    }

    return baseObjectives;
  }

  private identifyRequiredResources(skillTarget: string): string[] {
    return [
      'Motor control bandwidth',
      'Sensory feedback channels',
      'Processing capacity',
      'Memory allocation for skill storage',
      'Coordination with Treasury service'
    ];
  }

  private async handleBehaviorOptimization(message: ServiceMessage, startTime: number): Promise<ServiceMessage> {
    const { targetBehavior, currentEfficiency, constraints } = message.payload;

    const optimization = this.optimizeBehavior(targetBehavior, currentEfficiency, constraints);
    this.optimizationHistory.push(optimization);

    return createMessage(
      'BEHAVIOR_OPTIMIZED',
      {
        optimization,
        processingTime: Date.now() - startTime,
        source: this.config.serviceName
      },
      this.config.serviceName,
      message.source
    );
  }

  private optimizeBehavior(
    targetBehavior: string,
    currentEfficiency: number = 0.5,
    constraints?: any
  ): BehavioralOptimization {
    const optimizations: OptimizationAction[] = [
      {
        action: 'Streamline motor pathway connections',
        priority: 'high',
        effort: 0.3,
        impact: 0.4
      },
      {
        action: 'Reduce redundant processing steps',
        priority: 'medium',
        effort: 0.2,
        impact: 0.25
      },
      {
        action: 'Enhance sensory-motor feedback loop',
        priority: 'high',
        effort: 0.4,
        impact: 0.35
      },
      {
        action: 'Coordinate with Autonomic Process Director',
        priority: 'medium',
        effort: 0.2,
        impact: 0.2
      }
    ];

    const expectedImprovement = optimizations
      .reduce((sum, opt) => sum + opt.impact, 0) * (1 - currentEfficiency);

    return {
      id: `opt-${Date.now()}`,
      targetBehavior: targetBehavior || 'general-motor',
      currentEfficiency,
      optimizations,
      expectedImprovement: Math.min(expectedImprovement, 1 - currentEfficiency),
      parasympatheticCoordination: true
    };
  }

  private async handleResourceAllocation(message: ServiceMessage, startTime: number): Promise<ServiceMessage> {
    const { resourceType, amount, targets } = message.payload;

    const allocation = this.allocateResources(resourceType, amount, targets);

    return createMessage(
      'RESOURCES_ALLOCATED',
      {
        allocation,
        processingTime: Date.now() - startTime,
        source: this.config.serviceName
      },
      this.config.serviceName,
      message.source
    );
  }

  private allocateResources(resourceType: string, amount?: number, targets?: string[]): ResourceAllocation {
    const existing = this.resourceAllocations.get(resourceType);
    const available = existing?.available ?? 100;
    const toAllocate = Math.min(amount || 10, available);

    const allocation: ResourceAllocation = {
      id: `alloc-${Date.now()}`,
      resourceType: resourceType || 'general',
      allocated: (existing?.allocated ?? 0) + toAllocate,
      available: available - toAllocate,
      utilization: ((existing?.allocated ?? 0) + toAllocate) / 100,
      targets: targets || ['motor-control', 'behavioral-processing']
    };

    this.resourceAllocations.set(resourceType, allocation);

    return allocation;
  }

  private async handleParasympatheticCoordination(message: ServiceMessage, startTime: number): Promise<ServiceMessage> {
    const { coordinationType, targetTriad, payload } = message.payload;

    const coordination = this.coordinateParasympathetic(coordinationType, targetTriad, payload);
    this.sharedParasympatheticState.set(coordinationType, coordination);

    return createMessage(
      'PARASYMPATHETIC_COORDINATED',
      {
        coordination,
        sharedWith: targetTriad || 'autonomic',
        processingTime: Date.now() - startTime,
        source: this.config.serviceName
      },
      this.config.serviceName,
      message.source
    );
  }

  private coordinateParasympathetic(
    coordinationType: string,
    targetTriad?: string,
    payload?: any
  ): any {
    return {
      id: `coord-${Date.now()}`,
      type: coordinationType || 'general',
      sourceTriad: 'somatic',
      targetTriad: targetTriad || 'autonomic',
      sharedState: {
        motorDevelopmentActive: this.developmentPlans.size > 0,
        activeOptimizations: this.optimizationHistory.length,
        resourceUtilization: this.calculateOverallUtilization(),
        coordinationTimestamp: new Date()
      },
      actions: [
        'Synchronize motor development with autonomic background processing',
        'Share resource allocation state for system-wide optimization',
        'Coordinate skill storage with Treasury service'
      ],
      bidirectional: true
    };
  }

  private calculateOverallUtilization(): number {
    const allocations = Array.from(this.resourceAllocations.values());
    if (allocations.length === 0) return 0;
    return allocations.reduce((sum, a) => sum + a.utilization, 0) / allocations.length;
  }

  private async handleGetDevelopmentStatus(message: ServiceMessage, startTime: number): Promise<ServiceMessage> {
    const { planId } = message.payload;

    let status: any;
    if (planId) {
      const plan = this.developmentPlans.get(planId);
      status = plan ? { plan, found: true } : { found: false, planId };
    } else {
      status = {
        totalPlans: this.developmentPlans.size,
        activePlans: Array.from(this.developmentPlans.values()).filter(p => p.status === 'active').length,
        plans: Array.from(this.developmentPlans.values()),
        optimizationCount: this.optimizationHistory.length,
        resourceUtilization: this.calculateOverallUtilization()
      };
    }

    return createMessage(
      'DEVELOPMENT_STATUS_RETRIEVED',
      {
        status,
        processingTime: Date.now() - startTime,
        source: this.config.serviceName
      },
      this.config.serviceName,
      message.source
    );
  }

  private async handleUpdateSkillProgress(message: ServiceMessage, startTime: number): Promise<ServiceMessage> {
    const { planId, stageId, progress } = message.payload;

    const plan = this.developmentPlans.get(planId);
    if (!plan) {
      return createMessage(
        'SKILL_PROGRESS_ERROR',
        {
          error: 'Plan not found',
          planId,
          processingTime: Date.now() - startTime,
          source: this.config.serviceName
        },
        this.config.serviceName,
        message.source
      );
    }

    const stage = plan.stages.find(s => s.id === stageId);
    if (stage) {
      stage.progress = Math.min(progress || 0, 100);
    }

    // Check if plan is complete
    const allStagesComplete = plan.stages.every(s => s.progress >= 100);
    if (allStagesComplete) {
      plan.status = 'completed';
    } else if (plan.status === 'planning') {
      plan.status = 'active';
    }

    return createMessage(
      'SKILL_PROGRESS_UPDATED',
      {
        planId,
        stageId,
        newProgress: stage?.progress,
        planStatus: plan.status,
        treasurySync: stage?.progress === 100 ? 'Skill ready for Treasury storage' : null,
        processingTime: Date.now() - startTime,
        source: this.config.serviceName
      },
      this.config.serviceName,
      message.source
    );
  }

  private initializeDevelopmentFramework(): void {
    // Initialize default resource pools
    const resourceTypes = ['motor-bandwidth', 'processing-capacity', 'memory-allocation', 'coordination-channels'];

    resourceTypes.forEach(type => {
      this.resourceAllocations.set(type, {
        id: `default-${type}`,
        resourceType: type,
        allocated: 0,
        available: 100,
        utilization: 0,
        targets: []
      });
    });

    // Initialize shared parasympathetic state
    this.sharedParasympatheticState.set('initialized', {
      timestamp: new Date(),
      status: 'ready',
      connectedTriads: ['somatic', 'autonomic']
    });
  }

  async shutdown(): Promise<void> {
    this.log('info', 'Shutting down Development Service');
    // Notify Autonomic triad of shutdown
    this.sharedParasympatheticState.set('shutdown', {
      timestamp: new Date(),
      reason: 'graceful-shutdown'
    });
  }
}
