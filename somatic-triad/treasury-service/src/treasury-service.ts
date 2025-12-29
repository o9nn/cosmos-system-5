import { BaseService, ServiceConfig, ServiceMessage, createMessage } from '@cosmos/cognitive-core-shared-libraries';

interface MotorMemory {
  id: string;
  skillName: string;
  skillType: 'procedural' | 'motor' | 'behavioral' | 'reflexive';
  pattern: MotorPattern;
  proficiency: number;
  lastAccessed: Date;
  accessCount: number;
  metadata: SkillMetadata;
}

interface MotorPattern {
  sequence: string[];
  timing: number[];
  precision: number;
  adaptability: number;
}

interface SkillMetadata {
  createdAt: Date;
  developmentPlanId?: string;
  sourceTriad: string;
  validatedBy: string[];
  dependencies: string[];
}

interface LearnedSkill {
  id: string;
  name: string;
  category: string;
  proficiencyLevel: number;
  patterns: string[];
  integrations: SkillIntegration[];
}

interface SkillIntegration {
  targetService: string;
  integrationType: 'motor' | 'sensory' | 'behavioral';
  strength: number;
}

interface SkillRetrievalResult {
  skill: MotorMemory | null;
  retrievalTime: number;
  confidence: number;
  alternatives: string[];
}

export class TreasuryService extends BaseService {
  private motorMemoryStore: Map<string, MotorMemory>;
  private learnedSkills: Map<string, LearnedSkill>;
  private accessLog: Array<{ skillId: string; timestamp: Date; success: boolean }>;
  private sharedParasympatheticState: Map<string, any>;

  constructor(config: ServiceConfig) {
    super(config);
    this.motorMemoryStore = new Map();
    this.learnedSkills = new Map();
    this.accessLog = [];
    this.sharedParasympatheticState = new Map();
    this.initializeTreasuryFramework();
  }

  async initialize(): Promise<void> {
    this.log('info', 'Initializing Treasury Service (T-7) - Potential Dimension [2-7]');
    this.log('info', 'Shared Parasympathetic Polarity: Receiving from Development (PD-2)');
    this.log('info', 'Treasury Service initialized - Motor memory and learned skills ready');
  }

  async process(message: ServiceMessage): Promise<ServiceMessage | null> {
    const startTime = Date.now();
    this.log('info', 'Processing treasury request', { messageId: message.id, type: message.type });

    try {
      switch (message.type) {
        case 'STORE_MOTOR_MEMORY':
          return this.handleStoreMotorMemory(message, startTime);

        case 'RETRIEVE_SKILL':
          return this.handleRetrieveSkill(message, startTime);

        case 'REGISTER_LEARNED_SKILL':
          return this.handleRegisterLearnedSkill(message, startTime);

        case 'UPDATE_PROFICIENCY':
          return this.handleUpdateProficiency(message, startTime);

        case 'GET_SKILL_INVENTORY':
          return this.handleGetSkillInventory(message, startTime);

        case 'RECEIVE_FROM_DEVELOPMENT':
          return this.handleReceiveFromDevelopment(message, startTime);

        case 'INTEGRATE_SKILL':
          return this.handleSkillIntegration(message, startTime);

        default:
          this.log('warn', 'Unknown message type', { type: message.type });
          return null;
      }
    } catch (error) {
      this.log('error', 'Error processing treasury request', { error, messageId: message.id });
      throw error;
    }
  }

  private async handleStoreMotorMemory(message: ServiceMessage, startTime: number): Promise<ServiceMessage> {
    const { skillName, skillType, pattern, proficiency, metadata } = message.payload;

    const memory = this.storeMotorMemory(skillName, skillType, pattern, proficiency, metadata);
    this.motorMemoryStore.set(memory.id, memory);

    return createMessage(
      'MOTOR_MEMORY_STORED',
      {
        memory: {
          id: memory.id,
          skillName: memory.skillName,
          proficiency: memory.proficiency,
          storedAt: memory.metadata.createdAt
        },
        processingTime: Date.now() - startTime,
        source: this.config.serviceName
      },
      this.config.serviceName,
      message.source
    );
  }

  private storeMotorMemory(
    skillName: string,
    skillType?: string,
    pattern?: Partial<MotorPattern>,
    proficiency?: number,
    metadata?: Partial<SkillMetadata>
  ): MotorMemory {
    const memory: MotorMemory = {
      id: `mm-${Date.now()}`,
      skillName: skillName || 'unnamed-skill',
      skillType: (skillType as any) || 'motor',
      pattern: {
        sequence: pattern?.sequence || [],
        timing: pattern?.timing || [],
        precision: pattern?.precision ?? 0.7,
        adaptability: pattern?.adaptability ?? 0.5
      },
      proficiency: proficiency ?? 0.5,
      lastAccessed: new Date(),
      accessCount: 0,
      metadata: {
        createdAt: new Date(),
        developmentPlanId: metadata?.developmentPlanId,
        sourceTriad: metadata?.sourceTriad || 'somatic',
        validatedBy: metadata?.validatedBy || [],
        dependencies: metadata?.dependencies || []
      }
    };

    return memory;
  }

  private async handleRetrieveSkill(message: ServiceMessage, startTime: number): Promise<ServiceMessage> {
    const { skillId, skillName, skillType } = message.payload;

    const result = this.retrieveSkill(skillId, skillName, skillType);

    this.accessLog.push({
      skillId: skillId || skillName || 'search',
      timestamp: new Date(),
      success: result.skill !== null
    });

    return createMessage(
      'SKILL_RETRIEVED',
      {
        result,
        processingTime: Date.now() - startTime,
        source: this.config.serviceName
      },
      this.config.serviceName,
      message.source
    );
  }

  private retrieveSkill(skillId?: string, skillName?: string, skillType?: string): SkillRetrievalResult {
    const startTime = Date.now();
    let skill: MotorMemory | null = null;
    const alternatives: string[] = [];

    // Search by ID first
    if (skillId && this.motorMemoryStore.has(skillId)) {
      skill = this.motorMemoryStore.get(skillId)!;
    } else {
      // Search by name
      for (const [id, memory] of this.motorMemoryStore) {
        if (skillName && memory.skillName.toLowerCase().includes(skillName.toLowerCase())) {
          if (!skill || memory.proficiency > skill.proficiency) {
            skill = memory;
          }
          alternatives.push(memory.skillName);
        } else if (skillType && memory.skillType === skillType) {
          alternatives.push(memory.skillName);
        }
      }
    }

    if (skill) {
      skill.lastAccessed = new Date();
      skill.accessCount++;
    }

    return {
      skill,
      retrievalTime: Date.now() - startTime,
      confidence: skill ? skill.proficiency : 0,
      alternatives: alternatives.filter(a => a !== skill?.skillName).slice(0, 5)
    };
  }

  private async handleRegisterLearnedSkill(message: ServiceMessage, startTime: number): Promise<ServiceMessage> {
    const { name, category, proficiencyLevel, patterns, integrations } = message.payload;

    const skill = this.registerLearnedSkill(name, category, proficiencyLevel, patterns, integrations);
    this.learnedSkills.set(skill.id, skill);

    return createMessage(
      'LEARNED_SKILL_REGISTERED',
      {
        skill,
        processingTime: Date.now() - startTime,
        source: this.config.serviceName
      },
      this.config.serviceName,
      message.source
    );
  }

  private registerLearnedSkill(
    name: string,
    category?: string,
    proficiencyLevel?: number,
    patterns?: string[],
    integrations?: SkillIntegration[]
  ): LearnedSkill {
    return {
      id: `ls-${Date.now()}`,
      name: name || 'unnamed-learned-skill',
      category: category || 'general',
      proficiencyLevel: proficiencyLevel ?? 0.5,
      patterns: patterns || [],
      integrations: integrations || [
        { targetService: 'motor-control', integrationType: 'motor', strength: 0.7 },
        { targetService: 'processing-service', integrationType: 'behavioral', strength: 0.5 }
      ]
    };
  }

  private async handleUpdateProficiency(message: ServiceMessage, startTime: number): Promise<ServiceMessage> {
    const { skillId, newProficiency, reason } = message.payload;

    const memory = this.motorMemoryStore.get(skillId);
    if (!memory) {
      return createMessage(
        'PROFICIENCY_UPDATE_ERROR',
        {
          error: 'Skill not found',
          skillId,
          processingTime: Date.now() - startTime,
          source: this.config.serviceName
        },
        this.config.serviceName,
        message.source
      );
    }

    const oldProficiency = memory.proficiency;
    memory.proficiency = Math.max(0, Math.min(1, newProficiency ?? memory.proficiency));

    return createMessage(
      'PROFICIENCY_UPDATED',
      {
        skillId,
        oldProficiency,
        newProficiency: memory.proficiency,
        change: memory.proficiency - oldProficiency,
        reason: reason || 'manual update',
        processingTime: Date.now() - startTime,
        source: this.config.serviceName
      },
      this.config.serviceName,
      message.source
    );
  }

  private async handleGetSkillInventory(message: ServiceMessage, startTime: number): Promise<ServiceMessage> {
    const { category, minProficiency } = message.payload;

    const inventory = this.getSkillInventory(category, minProficiency);

    return createMessage(
      'SKILL_INVENTORY_RETRIEVED',
      {
        inventory,
        processingTime: Date.now() - startTime,
        source: this.config.serviceName
      },
      this.config.serviceName,
      message.source
    );
  }

  private getSkillInventory(category?: string, minProficiency?: number): any {
    const memories = Array.from(this.motorMemoryStore.values());
    const skills = Array.from(this.learnedSkills.values());

    let filteredMemories = memories;
    let filteredSkills = skills;

    if (category) {
      filteredSkills = skills.filter(s => s.category === category);
    }

    if (minProficiency !== undefined) {
      filteredMemories = memories.filter(m => m.proficiency >= minProficiency);
      filteredSkills = filteredSkills.filter(s => s.proficiencyLevel >= minProficiency);
    }

    const recentAccess = this.accessLog.slice(-100);
    const accessStats = {
      totalAccesses: recentAccess.length,
      successRate: recentAccess.filter(a => a.success).length / Math.max(recentAccess.length, 1)
    };

    return {
      totalMotorMemories: memories.length,
      totalLearnedSkills: skills.length,
      filteredMotorMemories: filteredMemories.length,
      filteredLearnedSkills: filteredSkills.length,
      motorMemories: filteredMemories.map(m => ({
        id: m.id,
        name: m.skillName,
        type: m.skillType,
        proficiency: m.proficiency,
        accessCount: m.accessCount
      })),
      learnedSkills: filteredSkills.map(s => ({
        id: s.id,
        name: s.name,
        category: s.category,
        proficiency: s.proficiencyLevel
      })),
      accessStatistics: accessStats,
      parasympatheticStatus: this.sharedParasympatheticState.get('status') || 'active'
    };
  }

  private async handleReceiveFromDevelopment(message: ServiceMessage, startTime: number): Promise<ServiceMessage> {
    const { developmentPlanId, completedSkill, pattern, proficiency } = message.payload;

    // Store the developed skill as motor memory
    const memory = this.storeMotorMemory(
      completedSkill?.name || `dev-skill-${developmentPlanId}`,
      completedSkill?.type || 'motor',
      pattern,
      proficiency,
      {
        developmentPlanId,
        sourceTriad: 'somatic',
        validatedBy: ['development-service']
      }
    );

    this.motorMemoryStore.set(memory.id, memory);

    // Update shared parasympathetic state
    this.sharedParasympatheticState.set('lastDevelopmentReceived', {
      timestamp: new Date(),
      planId: developmentPlanId,
      memoryId: memory.id
    });

    return createMessage(
      'DEVELOPMENT_RECEIVED',
      {
        memoryId: memory.id,
        skillName: memory.skillName,
        proficiency: memory.proficiency,
        developmentPlanId,
        parasympatheticSync: 'complete',
        processingTime: Date.now() - startTime,
        source: this.config.serviceName
      },
      this.config.serviceName,
      message.source
    );
  }

  private async handleSkillIntegration(message: ServiceMessage, startTime: number): Promise<ServiceMessage> {
    const { skillId, targetService, integrationType } = message.payload;

    const skill = this.learnedSkills.get(skillId);
    if (!skill) {
      return createMessage(
        'SKILL_INTEGRATION_ERROR',
        {
          error: 'Skill not found',
          skillId,
          processingTime: Date.now() - startTime,
          source: this.config.serviceName
        },
        this.config.serviceName,
        message.source
      );
    }

    const integration: SkillIntegration = {
      targetService: targetService || 'motor-control',
      integrationType: integrationType || 'motor',
      strength: 0.5
    };

    skill.integrations.push(integration);

    return createMessage(
      'SKILL_INTEGRATED',
      {
        skillId,
        skillName: skill.name,
        integration,
        totalIntegrations: skill.integrations.length,
        processingTime: Date.now() - startTime,
        source: this.config.serviceName
      },
      this.config.serviceName,
      message.source
    );
  }

  private initializeTreasuryFramework(): void {
    // Initialize some default motor memories
    const defaultSkills = [
      { name: 'basic-motor-control', type: 'motor', proficiency: 0.9 },
      { name: 'sensory-motor-coordination', type: 'procedural', proficiency: 0.8 },
      { name: 'adaptive-response', type: 'behavioral', proficiency: 0.7 },
      { name: 'reflex-action', type: 'reflexive', proficiency: 0.95 }
    ];

    defaultSkills.forEach(skill => {
      const memory = this.storeMotorMemory(skill.name, skill.type, undefined, skill.proficiency);
      this.motorMemoryStore.set(memory.id, memory);
    });

    // Initialize shared parasympathetic state
    this.sharedParasympatheticState.set('status', 'active');
    this.sharedParasympatheticState.set('initialized', {
      timestamp: new Date(),
      receivingFrom: 'development-service',
      connectedTriads: ['somatic', 'autonomic']
    });
  }

  async shutdown(): Promise<void> {
    this.log('info', 'Shutting down Treasury Service');
    this.sharedParasympatheticState.set('status', 'shutting-down');
  }
}
