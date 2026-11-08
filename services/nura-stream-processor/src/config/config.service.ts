import { Injectable, Logger } from '@nestjs/common';

/**
 * Configuration Service
 *
 * Centralized configuration management for all environment variables
 * Makes it easy to track all required env vars per service
 */
@Injectable()
export class ConfigService {
  private readonly logger = new Logger(ConfigService.name);

  // NATS Configuration
  readonly NATS_URL: string;

  // PostgreSQL Configuration
  readonly POSTGRES_HOST: string;
  readonly POSTGRES_PORT: number;
  readonly POSTGRES_DB: string;
  readonly POSTGRES_USER: string;
  readonly POSTGRES_PASSWORD: string;

  // VLM Service Configuration
  readonly VLM_SERVICE_URL: string;

  // Frigate Configuration
  readonly FRIGATE_URL: string;

  // Redis Configuration (for future use)
  readonly REDIS_HOST: string;
  readonly REDIS_PORT: number;

  // Processing Configuration
  readonly ACTIVITY_CLASSIFIER_ENABLED: boolean;
  readonly FACE_RECOGNITION_ENABLED: boolean;
  readonly UNKNOWN_PERSON_TRACKING_ENABLED: boolean;

  // Performance Configuration
  readonly DB_POOL_SIZE: number;
  readonly AI_REQUEST_TIMEOUT: number;

  constructor() {
    // NATS
    this.NATS_URL = process.env.NATS_URL || 'nats://localhost:4222';

    // PostgreSQL
    this.POSTGRES_HOST = process.env.POSTGRES_HOST || 'localhost';
    this.POSTGRES_PORT = parseInt(process.env.POSTGRES_PORT || '5432');
    this.POSTGRES_DB = process.env.POSTGRES_DB || 'nura_db';
    this.POSTGRES_USER = process.env.POSTGRES_USER || 'nura';
    this.POSTGRES_PASSWORD = process.env.POSTGRES_PASSWORD || 'PaSSw0rd!';

    // VLM Service
    this.VLM_SERVICE_URL = process.env.VLM_SERVICE_URL || 'http://localhost:8001';

    // Frigate
    this.FRIGATE_URL = process.env.FRIGATE_URL || 'http://localhost:5000';

    // Redis
    this.REDIS_HOST = process.env.REDIS_HOST || 'localhost';
    this.REDIS_PORT = parseInt(process.env.REDIS_PORT || '6379');

    // Processing Features
    this.ACTIVITY_CLASSIFIER_ENABLED = process.env.ACTIVITY_CLASSIFIER_ENABLED !== 'false';
    this.FACE_RECOGNITION_ENABLED = process.env.FACE_RECOGNITION_ENABLED !== 'false';
    this.UNKNOWN_PERSON_TRACKING_ENABLED = process.env.UNKNOWN_PERSON_TRACKING_ENABLED !== 'false';

    // Performance
    this.DB_POOL_SIZE = parseInt(process.env.DB_POOL_SIZE || '10');
    this.AI_REQUEST_TIMEOUT = parseInt(process.env.AI_REQUEST_TIMEOUT || '120000');

    this.logConfiguration();
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
   * Get Redis connection config
   */
  getRedisConfig() {
    return {
      host: this.REDIS_HOST,
      port: this.REDIS_PORT,
    };
  }

  /**
   * Log loaded configuration (without sensitive data)
   */
  private logConfiguration() {
    this.logger.log('📋 Configuration loaded:');
    this.logger.log(`  NATS: ${this.NATS_URL}`);
    this.logger.log(`  PostgreSQL: ${this.POSTGRES_USER}@${this.POSTGRES_HOST}:${this.POSTGRES_PORT}/${this.POSTGRES_DB}`);
    this.logger.log(`  VLM Service: ${this.VLM_SERVICE_URL}`);
    this.logger.log(`  Frigate: ${this.FRIGATE_URL}`);
    this.logger.log(`  Redis: ${this.REDIS_HOST}:${this.REDIS_PORT}`);
    this.logger.log(`  Activity Classifier: ${this.ACTIVITY_CLASSIFIER_ENABLED ? '✅' : '❌'}`);
    this.logger.log(`  Face Recognition: ${this.FACE_RECOGNITION_ENABLED ? '✅' : '❌'}`);
    this.logger.log(`  Unknown Tracking: ${this.UNKNOWN_PERSON_TRACKING_ENABLED ? '✅' : '❌'}`);
  }

  /**
   * Validate required environment variables
   */
  validateConfig(): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (!this.POSTGRES_PASSWORD || this.POSTGRES_PASSWORD === 'PaSSw0rd!') {
      errors.push('⚠️  Using default PostgreSQL password - set POSTGRES_PASSWORD in .env');
    }

    if (!this.NATS_URL) {
      errors.push('❌ NATS_URL is required');
    }

    if (!this.VLM_SERVICE_URL) {
      errors.push('❌ VLM_SERVICE_URL is required');
    }

    if (errors.length > 0) {
      errors.forEach(err => this.logger.warn(err));
    }

    return {
      valid: errors.filter(e => e.startsWith('❌')).length === 0,
      errors,
    };
  }
}
