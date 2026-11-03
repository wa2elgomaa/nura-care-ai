import {
  Controller,
  Get,
  Post,
  Patch,
  Delete,
  Body,
  Param,
  Query,
  HttpCode,
  HttpStatus,
  Logger,
} from '@nestjs/common';
import { RulesService, MatchRequest, MatchResponse, Rule } from './rules.service.js';

/**
 * Rules Controller
 * REST API for RAG rule matching and management
 * Spec: specs/023-rag-rule-knowledge/spec.md
 */
@Controller()
export class RulesController {
  private readonly logger = new Logger(RulesController.name);

  constructor(private readonly rulesService: RulesService) {}

  /**
   * Health check
   */
  @Get('health')
  health() {
    return {
      status: 'healthy',
      service: 'nura-rag',
      version: '0.1.0',
    };
  }

  /**
   * FR-001: Match event context to rules
   * POST /match
   */
  @Post('match')
  @HttpCode(HttpStatus.OK)
  async matchRules(@Body() request: MatchRequest): Promise<MatchResponse> {
    this.logger.log(`Matching rules for context: "${request.event_context.substring(0, 50)}..."`);
    return this.rulesService.matchRules(request);
  }

  /**
   * Get all rules with optional filters
   * GET /rules?category=supervision&severity=critical&enabled=true
   */
  @Get('rules')
  async getRules(
    @Query('category') category?: string,
    @Query('severity') severity?: string,
    @Query('enabled') enabled?: string,
  ): Promise<Rule[]> {
    return this.rulesService.getRules({
      category,
      severity,
      enabled: enabled ? enabled === 'true' : undefined,
    });
  }

  /**
   * Get rule by ID
   * GET /rules/:ruleId
   */
  @Get('rules/:ruleId')
  async getRule(@Param('ruleId') ruleId: string): Promise<Rule> {
    const rule = await this.rulesService.getRule(ruleId);
    if (!rule) {
      throw new Error(`Rule not found: ${ruleId}`);
    }
    return rule;
  }

  /**
   * Create new rule
   * POST /rules
   */
  @Post('rules')
  @HttpCode(HttpStatus.CREATED)
  async createRule(
    @Body() rule: Omit<Rule, 'id' | 'created_at' | 'updated_at'>,
  ): Promise<Rule> {
    return this.rulesService.createRule(rule);
  }

  /**
   * Update rule
   * PATCH /rules/:ruleId
   */
  @Patch('rules/:ruleId')
  async updateRule(
    @Param('ruleId') ruleId: string,
    @Body() updates: Partial<Omit<Rule, 'id' | 'created_at' | 'updated_at'>>,
  ): Promise<Rule> {
    return this.rulesService.updateRule(ruleId, updates);
  }

  /**
   * Delete (disable) rule
   * DELETE /rules/:ruleId
   */
  @Delete('rules/:ruleId')
  @HttpCode(HttpStatus.NO_CONTENT)
  async deleteRule(@Param('ruleId') ruleId: string): Promise<void> {
    await this.rulesService.deleteRule(ruleId);
  }

  /**
   * Root endpoint
   */
  @Get()
  root() {
    return {
      service: 'nura-rag',
      description: 'Rule knowledge base with semantic similarity search (pgvector)',
      version: '0.1.0',
      spec: 'specs/023-rag-rule-knowledge/spec.md',
      endpoints: {
        'POST /match': 'Match event context to rules',
        'GET /rules': 'List all rules (with filters)',
        'GET /rules/:id': 'Get rule by ID',
        'POST /rules': 'Create new rule',
        'PATCH /rules/:id': 'Update rule',
        'DELETE /rules/:id': 'Delete (disable) rule',
      },
    };
  }
}
