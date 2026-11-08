import { Injectable, Logger } from '@nestjs/common';

/**
 * Configuration Service - nura-alerts
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

  // Frigate Configuration
  readonly FRIGATE_URL: string;

  // Alerting Configuration
  readonly SLACK_WEBHOOK_URL: string;
  readonly EMAIL_ENABLED: boolean;
  readonly SMS_ENABLED: boolean;
  readonly PUSH_NOTIFICATION_ENABLED: boolean;

  // Alert Severity Thresholds
  readonly ALERT_COOLDOWN_MINUTES: number;
  readonly HIGH_SEVERITY_COOLDOWN_MINUTES: number;

  // Performance Configuration
  readonly DB_POOL_SIZE: number;

  constructor() {
    // NATS
    this.NATS_URL = process.env.NATS_URL || 'nats://localhost:4222';

    // PostgreSQL
    this.POSTGRES_HOST = process.env.POSTGRES_HOST || 'localhost';
    this.POSTGRES_PORT = parseInt(process.env.POSTGRES_PORT || '5432');
    this.POSTGRES_DB = process.env.POSTGRES_DB || 'nura_db';
    this.POSTGRES_USER = process.env.POSTGRES_USER || 'nura';
    this.POSTGRES_PASSWORD = process.env.POSTGRES_PASSWORD || 'PaSSw0rd!';

    // Frigate
    this.FRIGATE_URL = process.env.FRIGATE_URL || 'http://localhost:5000';

    // Alerting Channels
    this.SLACK_WEBHOOK_URL = process.env.SLACK_WEBHOOK_URL || '';
    this.EMAIL_ENABLED = process.env.EMAIL_ENABLED === 'true';
    this.SMS_ENABLED = process.env.SMS_ENABLED === 'true';
    this.PUSH_NOTIFICATION_ENABLED = process.env.PUSH_NOTIFICATION_ENABLED === 'true';

    // Alert Thresholds
    this.ALERT_COOLDOWN_MINUTES = parseInt(process.env.ALERT_COOLDOWN_MINUTES || '5');
    this.HIGH_SEVERITY_COOLDOWN_MINUTES = parseInt(process.env.HIGH_SEVERITY_COOLDOWN_MINUTES || '1');

    // Performance
    this.DB_POOL_SIZE = parseInt(process.env.DB_POOL_SIZE || '10');

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
   * Check if any alert channel is enabled
   */
  hasAlertChannels(): boolean {
    return !!(this.SLACK_WEBHOOK_URL || this.EMAIL_ENABLED || this.SMS_ENABLED || this.PUSH_NOTIFICATION_ENABLED);
  }

  /**
   * Log loaded configuration (without sensitive data)
   */
  private logConfiguration() {
    this.logger.log('📋 Configuration loaded:');
    this.logger.log(`  NATS: ${this.NATS_URL}`);
    this.logger.log(`  PostgreSQL: ${this.POSTGRES_USER}@${this.POSTGRES_HOST}:${this.POSTGRES_PORT}/${this.POSTGRES_DB}`);
    this.logger.log(`  Frigate: ${this.FRIGATE_URL}`);
    this.logger.log(`  Slack: ${this.SLACK_WEBHOOK_URL ? '✅ Configured' : '❌ Not configured'}`);
    this.logger.log(`  Email: ${this.EMAIL_ENABLED ? '✅' : '❌'}`);
    this.logger.log(`  SMS: ${this.SMS_ENABLED ? '✅' : '❌'}`);
    this.logger.log(`  Push Notifications: ${this.PUSH_NOTIFICATION_ENABLED ? '✅' : '❌'}`);
    this.logger.log(`  Alert Cooldown: ${this.ALERT_COOLDOWN_MINUTES} min`);
    this.logger.log(`  High Severity Cooldown: ${this.HIGH_SEVERITY_COOLDOWN_MINUTES} min`);
  }

  /**
   * Validate required environment variables
   */
  validateConfig(): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (!this.NATS_URL) {
      errors.push('❌ NATS_URL is required');
    }

    if (!this.hasAlertChannels()) {
      errors.push('⚠️  No alert channels configured - alerts will not be sent');
    }

    if (!this.POSTGRES_PASSWORD || this.POSTGRES_PASSWORD === 'PaSSw0rd!') {
      errors.push('⚠️  Using default PostgreSQL password - set POSTGRES_PASSWORD in .env');
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
