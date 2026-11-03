import { Controller, Get, Post, Param, Body, Query, Logger } from '@nestjs/common';
import { ViolationsService } from './violations.service.js';

/**
 * Violations Controller
 * HTTP API for violation management
 */
@Controller()
export class ViolationsController {
  private readonly logger = new Logger(ViolationsController.name);

  constructor(private readonly violationsService: ViolationsService) {}

  @Get('health')
  health() {
    return {
      status: 'healthy',
      service: 'nura-rules',
      version: '0.1.0',
    };
  }

  @Get()
  root() {
    return {
      service: 'nura-rules',
      description: 'Rules engine for violation detection',
      version: '0.1.0',
      spec: 'specs/024-rules-engine-violation/spec.md',
    };
  }

  /**
   * Get recent violations
   */
  @Get('violations')
  async getViolations(@Query('limit') limit?: string) {
    const limitNum = limit ? parseInt(limit, 10) : 50;
    return this.violationsService.getRecentViolations(limitNum);
  }

  /**
   * Acknowledge violation
   */
  @Post('violations/:eventId/acknowledge')
  async acknowledgeViolation(
    @Param('eventId') eventId: string,
    @Body('acknowledged_by') acknowledgedBy: string,
  ) {
    await this.violationsService.acknowledgeViolation(eventId, acknowledgedBy);
    return { status: 'acknowledged' };
  }
}
