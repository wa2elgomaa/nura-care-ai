import { Injectable, Logger } from '@nestjs/common';

/**
 * Configuration Service - nura-rules
 * Centralized configuration management (all .env driven)
 */
@Injectable()
export class ConfigService {
  private readonly logger = new Logger(ConfigService.name);

  // Service Configuration
  readonly PORT: number;
  readonly SITE_ID: string;

  // Database Configuration
  readonly DATABASE_URL: string;

  // NATS Configuration
  readonly NATS_URL: string;

  // External Services
  readonly RAG_SERVICE_URL: string;
  readonly VLM_SERVICE_URL: string;

  // Threshold Configuration
  readonly SUPERVISION_THRESHOLD_SECONDS: number;
  readonly CAPACITY_THRESHOLD_PERCENT: number;
  readonly RESTRICTED_AREA_THRESHOLD_SECONDS: number;

  // RAG Configuration
  readonly RAG_SIMILARITY_THRESHOLD: number;
  readonly RAG_TOP_K: number;

  constructor() {
    // Service
    this.PORT = parseInt(process.env.PORT || '3003');
    this.SITE_ID = process.env.SITE_ID || 'dev-site-001';

    // Database
    this.DATABASE_URL = process.env.DATABASE_URL || 'postgresql://nura:PaSSw0rd!@postgres:5432/nura_db';

    // NATS
    this.NATS_URL = process.env.NATS_URL || 'nats://nats:4222';

    // External Services
    this.RAG_SERVICE_URL = process.env.RAG_SERVICE_URL || 'http://nura-rag:3002';
    this.VLM_SERVICE_URL = process.env.VLM_SERVICE_URL || 'http://host.docker.internal:8001';

    // Thresholds (duration-based violations)
    this.SUPERVISION_THRESHOLD_SECONDS = parseInt(process.env.SUPERVISION_THRESHOLD_SECONDS || '30');
    this.CAPACITY_THRESHOLD_PERCENT = parseFloat(process.env.CAPACITY_THRESHOLD_PERCENT || '1.0');
    this.RESTRICTED_AREA_THRESHOLD_SECONDS = parseInt(process.env.RESTRICTED_AREA_THRESHOLD_SECONDS || '5');

    // RAG Configuration
    this.RAG_SIMILARITY_THRESHOLD = parseFloat(process.env.RAG_SIMILARITY_THRESHOLD || '0.4');
    this.RAG_TOP_K = parseInt(process.env.RAG_TOP_K || '3');

    this.logConfiguration();
  }

  // Legacy getters for backwards compatibility
  get databaseUrl(): string {
    return this.DATABASE_URL;
  }

  get natsUrl(): string {
    return this.NATS_URL;
  }

  get ragServiceUrl(): string {
    return this.RAG_SERVICE_URL;
  }

  get vlmServiceUrl(): string {
    return this.VLM_SERVICE_URL;
  }

  get siteId(): string {
    return this.SITE_ID;
  }

  get supervisionThresholdSeconds(): number {
    return this.SUPERVISION_THRESHOLD_SECONDS;
  }

  /**
   * Log loaded configuration
   */
  private logConfiguration() {
    this.logger.log('📋 Rules Engine Configuration loaded:');
    this.logger.log(`  Port: ${this.PORT}`);
    this.logger.log(`  Site ID: ${this.SITE_ID}`);
    this.logger.log(`  Database: ${this.DATABASE_URL.split('@')[1]}`); // Hide password
    this.logger.log(`  NATS: ${this.NATS_URL}`);
    this.logger.log(`  RAG Service: ${this.RAG_SERVICE_URL}`);
    this.logger.log(`  VLM Service: ${this.VLM_SERVICE_URL}`);
    this.logger.log(`  Supervision Threshold: ${this.SUPERVISION_THRESHOLD_SECONDS}s`);
    this.logger.log(`  Capacity Threshold: ${this.CAPACITY_THRESHOLD_PERCENT * 100}%`);
    this.logger.log(`  Restricted Area Threshold: ${this.RESTRICTED_AREA_THRESHOLD_SECONDS}s`);
    this.logger.log(`  RAG Similarity: ${this.RAG_SIMILARITY_THRESHOLD} (top ${this.RAG_TOP_K})`);
  }

  /**
   * Validate configuration
   */
  validateConfig(): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (this.SUPERVISION_THRESHOLD_SECONDS < 1) {
      errors.push('❌ SUPERVISION_THRESHOLD_SECONDS must be >= 1');
    }

    if (this.CAPACITY_THRESHOLD_PERCENT < 0 || this.CAPACITY_THRESHOLD_PERCENT > 2) {
      errors.push('❌ CAPACITY_THRESHOLD_PERCENT must be between 0 and 2');
    }

    if (this.RAG_SIMILARITY_THRESHOLD < 0 || this.RAG_SIMILARITY_THRESHOLD > 1) {
      errors.push('❌ RAG_SIMILARITY_THRESHOLD must be between 0 and 1');
    }

    if (this.RAG_TOP_K < 1 || this.RAG_TOP_K > 10) {
      errors.push('❌ RAG_TOP_K must be between 1 and 10');
    }

    return {
      valid: errors.filter(e => e.startsWith('❌')).length === 0,
      errors,
    };
  }
}
