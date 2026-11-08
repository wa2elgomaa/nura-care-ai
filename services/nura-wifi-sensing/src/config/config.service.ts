import { Injectable, Logger } from '@nestjs/common';

/**
 * Configuration Service - nura-wifi-sensing
 *
 * Centralized configuration management for all environment variables
 * Makes it easy to track all required env vars per service
 */
@Injectable()
export class ConfigService {
  private readonly logger = new Logger(ConfigService.name);

  // MQTT Configuration (RuView ESP32 devices)
  readonly MQTT_BROKER_URL: string;
  readonly MQTT_USERNAME: string;
  readonly MQTT_PASSWORD: string;
  readonly MQTT_TOPICS: string[];

  // PostgreSQL Configuration
  readonly POSTGRES_HOST: string;
  readonly POSTGRES_PORT: number;
  readonly POSTGRES_DB: string;
  readonly POSTGRES_USER: string;
  readonly POSTGRES_PASSWORD: string;

  // NATS Configuration
  readonly NATS_URL: string;

  // WiFi Sensing Configuration
  readonly OCCUPANCY_THRESHOLD: number;
  readonly DETECTION_CONFIDENCE_MIN: number;
  readonly ROOM_MAPPING_ENABLED: boolean;
  readonly AFTER_HOURS_DETECTION_ENABLED: boolean;

  // After-Hours Configuration
  readonly FACILITY_OPEN_HOUR: number;
  readonly FACILITY_CLOSE_HOUR: number;

  // Multi-Occupancy Detection
  readonly MULTI_OCCUPANCY_THRESHOLD: number;
  readonly MULTI_OCCUPANCY_ALERT_ENABLED: boolean;

  // Performance Configuration
  readonly DB_POOL_SIZE: number;
  readonly EVENT_BATCH_SIZE: number;
  readonly EVENT_BATCH_INTERVAL_MS: number;

  constructor() {
    // MQTT
    this.MQTT_BROKER_URL = process.env.MQTT_BROKER_URL || 'mqtt://localhost:1883';
    this.MQTT_USERNAME = process.env.MQTT_USERNAME || '';
    this.MQTT_PASSWORD = process.env.MQTT_PASSWORD || '';
    this.MQTT_TOPICS = (process.env.MQTT_TOPICS || 'wifi/+/occupancy,wifi/+/presence').split(',');

    // PostgreSQL
    this.POSTGRES_HOST = process.env.POSTGRES_HOST || 'localhost';
    this.POSTGRES_PORT = parseInt(process.env.POSTGRES_PORT || '5432');
    this.POSTGRES_DB = process.env.POSTGRES_DB || 'nura_db';
    this.POSTGRES_USER = process.env.POSTGRES_USER || 'nura';
    this.POSTGRES_PASSWORD = process.env.POSTGRES_PASSWORD || 'PaSSw0rd!';

    // NATS
    this.NATS_URL = process.env.NATS_URL || 'nats://localhost:4222';

    // WiFi Sensing
    this.OCCUPANCY_THRESHOLD = parseInt(process.env.OCCUPANCY_THRESHOLD || '1');
    this.DETECTION_CONFIDENCE_MIN = parseFloat(process.env.DETECTION_CONFIDENCE_MIN || '0.7');
    this.ROOM_MAPPING_ENABLED = process.env.ROOM_MAPPING_ENABLED !== 'false';
    this.AFTER_HOURS_DETECTION_ENABLED = process.env.AFTER_HOURS_DETECTION_ENABLED !== 'false';

    // After-Hours
    this.FACILITY_OPEN_HOUR = parseInt(process.env.FACILITY_OPEN_HOUR || '7');
    this.FACILITY_CLOSE_HOUR = parseInt(process.env.FACILITY_CLOSE_HOUR || '18');

    // Multi-Occupancy
    this.MULTI_OCCUPANCY_THRESHOLD = parseInt(process.env.MULTI_OCCUPANCY_THRESHOLD || '2');
    this.MULTI_OCCUPANCY_ALERT_ENABLED = process.env.MULTI_OCCUPANCY_ALERT_ENABLED !== 'false';

    // Performance
    this.DB_POOL_SIZE = parseInt(process.env.DB_POOL_SIZE || '10');
    this.EVENT_BATCH_SIZE = parseInt(process.env.EVENT_BATCH_SIZE || '100');
    this.EVENT_BATCH_INTERVAL_MS = parseInt(process.env.EVENT_BATCH_INTERVAL_MS || '5000');

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
   * Get MQTT connection config
   */
  getMqttConfig() {
    return {
      url: this.MQTT_BROKER_URL,
      username: this.MQTT_USERNAME,
      password: this.MQTT_PASSWORD,
      topics: this.MQTT_TOPICS,
    };
  }

  /**
   * Check if current time is after hours
   */
  isAfterHours(): boolean {
    const now = new Date();
    const hour = now.getHours();
    return hour < this.FACILITY_OPEN_HOUR || hour >= this.FACILITY_CLOSE_HOUR;
  }

  /**
   * Log loaded configuration (without sensitive data)
   */
  private logConfiguration() {
    this.logger.log('📋 Configuration loaded:');
    this.logger.log(`  MQTT Broker: ${this.MQTT_BROKER_URL}`);
    this.logger.log(`  MQTT Topics: ${this.MQTT_TOPICS.join(', ')}`);
    this.logger.log(`  MQTT Auth: ${this.MQTT_USERNAME ? '✅' : '❌ (anonymous)'}`);
    this.logger.log(`  PostgreSQL: ${this.POSTGRES_USER}@${this.POSTGRES_HOST}:${this.POSTGRES_PORT}/${this.POSTGRES_DB}`);
    this.logger.log(`  NATS: ${this.NATS_URL}`);
    this.logger.log(`  Occupancy Threshold: ${this.OCCUPANCY_THRESHOLD} person(s)`);
    this.logger.log(`  Min Confidence: ${(this.DETECTION_CONFIDENCE_MIN * 100).toFixed(0)}%`);
    this.logger.log(`  Room Mapping: ${this.ROOM_MAPPING_ENABLED ? '✅' : '❌'}`);
    this.logger.log(`  After-Hours Detection: ${this.AFTER_HOURS_DETECTION_ENABLED ? '✅' : '❌'}`);
    this.logger.log(`  Facility Hours: ${this.FACILITY_OPEN_HOUR}:00 - ${this.FACILITY_CLOSE_HOUR}:00`);
    this.logger.log(`  Multi-Occupancy Threshold: ${this.MULTI_OCCUPANCY_THRESHOLD}+ people`);
    this.logger.log(`  Multi-Occupancy Alerts: ${this.MULTI_OCCUPANCY_ALERT_ENABLED ? '✅' : '❌'}`);
    this.logger.log(`  Event Batching: ${this.EVENT_BATCH_SIZE} events / ${this.EVENT_BATCH_INTERVAL_MS}ms`);
  }

  /**
   * Validate required environment variables
   */
  validateConfig(): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (!this.MQTT_BROKER_URL) {
      errors.push('❌ MQTT_BROKER_URL is required');
    }

    if (!this.NATS_URL) {
      errors.push('❌ NATS_URL is required');
    }

    if (!this.POSTGRES_PASSWORD || this.POSTGRES_PASSWORD === 'PaSSw0rd!') {
      errors.push('⚠️  Using default PostgreSQL password - set POSTGRES_PASSWORD in .env');
    }

    if (this.FACILITY_OPEN_HOUR >= this.FACILITY_CLOSE_HOUR) {
      errors.push('⚠️  Invalid facility hours: FACILITY_OPEN_HOUR must be < FACILITY_CLOSE_HOUR');
    }

    if (this.MQTT_TOPICS.length === 0) {
      errors.push('⚠️  No MQTT topics configured - no events will be received');
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
