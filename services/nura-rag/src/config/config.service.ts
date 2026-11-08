import { Injectable, Logger } from '@nestjs/common';

/**
 * Configuration Service - nura-rag
 * Centralized configuration management (all .env driven)
 */
@Injectable()
export class ConfigService {
  private readonly logger = new Logger(ConfigService.name);

  // PostgreSQL Configuration
  readonly POSTGRES_HOST: string;
  readonly POSTGRES_PORT: number;
  readonly POSTGRES_DB: string;
  readonly POSTGRES_USER: string;
  readonly POSTGRES_PASSWORD: string;

  // RAG Configuration
  readonly PORT: number;
  readonly EMBEDDING_MODEL: string;
  readonly EMBEDDING_DIMENSIONS: number = 384; // all-MiniLM-L6-v2
  readonly SIMILARITY_THRESHOLD: number;
  readonly SITE_ID: string;

  // Performance
  readonly DB_POOL_SIZE: number;

  constructor() {
    // PostgreSQL
    this.POSTGRES_HOST = process.env.POSTGRES_HOST || 'localhost';
    this.POSTGRES_PORT = parseInt(process.env.POSTGRES_PORT || '5432');
    this.POSTGRES_DB = process.env.POSTGRES_DB || 'nura_db';
    this.POSTGRES_USER = process.env.POSTGRES_USER || 'nura';
    this.POSTGRES_PASSWORD = process.env.POSTGRES_PASSWORD || 'PaSSw0rd!';

    // RAG
    this.PORT = parseInt(process.env.PORT || '3002');
    this.EMBEDDING_MODEL = process.env.EMBEDDING_MODEL || 'Xenova/all-MiniLM-L6-v2';
    this.SIMILARITY_THRESHOLD = parseFloat(process.env.SIMILARITY_THRESHOLD || '0.7');
    this.SITE_ID = process.env.SITE_ID || 'dev-site-001';

    // Performance
    this.DB_POOL_SIZE = parseInt(process.env.DB_POOL_SIZE || '10');

    this.logConfiguration();
  }

  // Legacy getters for backwards compatibility
  get databaseUrl(): string {
    // Prioritize DATABASE_URL env var (injected by compose), otherwise construct from parts
    return process.env.DATABASE_URL || `postgresql://${this.POSTGRES_USER}:${this.POSTGRES_PASSWORD}@${this.POSTGRES_HOST}:${this.POSTGRES_PORT}/${this.POSTGRES_DB}`;
  }

  get embeddingModel(): string {
    return this.EMBEDDING_MODEL;
  }

  get embeddingDimensions(): number {
    return this.EMBEDDING_DIMENSIONS;
  }

  get similarityThreshold(): number {
    return this.SIMILARITY_THRESHOLD;
  }

  get siteId(): string {
    return this.SITE_ID;
  }

  /**
   * Get database connection config
   */
  getDatabaseConfig() {
    return {
      host: this.POSTGRES_HOST,
      port: this.POSTGRES_PORT,
      database: this.POSTGRES_DB,
      user: this.POSTGRES_USER,
      password: this.POSTGRES_PASSWORD,
      max: this.DB_POOL_SIZE,
      idleTimeoutMillis: 30000,
    };
  }

  /**
   * Log loaded configuration
   */
  private logConfiguration() {
    this.logger.log('📋 RAG Configuration loaded:');
    this.logger.log(`  Port: ${this.PORT}`);
    this.logger.log(`  PostgreSQL: ${this.POSTGRES_USER}@${this.POSTGRES_HOST}:${this.POSTGRES_PORT}/${this.POSTGRES_DB}`);
    this.logger.log(`  Embedding Model: ${this.EMBEDDING_MODEL}`);
    this.logger.log(`  Similarity Threshold: ${this.SIMILARITY_THRESHOLD}`);
    this.logger.log(`  Site ID: ${this.SITE_ID}`);
  }

  /**
   * Validate configuration
   */
  validateConfig(): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (!this.POSTGRES_PASSWORD || this.POSTGRES_PASSWORD === 'PaSSw0rd!') {
      errors.push('⚠️  Using default PostgreSQL password');
    }

    if (this.SIMILARITY_THRESHOLD < 0 || this.SIMILARITY_THRESHOLD > 1) {
      errors.push('❌ SIMILARITY_THRESHOLD must be between 0 and 1');
    }

    return {
      valid: errors.filter(e => e.startsWith('❌')).length === 0,
      errors,
    };
  }
}
