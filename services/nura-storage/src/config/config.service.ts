import { Injectable, Logger } from '@nestjs/common';

/**
 * Configuration Service - nura-storage
 *
 * Centralized configuration management for all environment variables
 * Makes it easy to track all required env vars per service
 */
@Injectable()
export class ConfigService {
  private readonly logger = new Logger(ConfigService.name);

  // Storage Backend Configuration
  readonly STORAGE_BACKEND: 'local' | 's3' | 'gcs' | 'azure';
  readonly STORAGE_BASE_PATH: string;

  // Local Storage Configuration
  readonly LOCAL_STORAGE_PATH: string;

  // S3 Configuration
  readonly S3_BUCKET: string;
  readonly S3_REGION: string;
  readonly S3_ACCESS_KEY_ID: string;
  readonly S3_SECRET_ACCESS_KEY: string;
  readonly S3_ENDPOINT: string;

  // Google Cloud Storage Configuration
  readonly GCS_BUCKET: string;
  readonly GCS_PROJECT_ID: string;
  readonly GCS_CREDENTIALS_PATH: string;

  // Azure Blob Storage Configuration
  readonly AZURE_STORAGE_ACCOUNT: string;
  readonly AZURE_STORAGE_KEY: string;
  readonly AZURE_CONTAINER: string;

  // API Configuration
  readonly PORT: number;
  readonly API_KEY: string;
  readonly CORS_ENABLED: boolean;

  // File Upload Configuration
  readonly MAX_FILE_SIZE_MB: number;
  readonly ALLOWED_MIME_TYPES: string[];
  readonly TEMP_UPLOAD_PATH: string;

  constructor() {
    // Storage Backend
    this.STORAGE_BACKEND = (process.env.STORAGE_BACKEND || 'local') as any;
    this.STORAGE_BASE_PATH = process.env.STORAGE_BASE_PATH || '/data/storage';

    // Local Storage
    this.LOCAL_STORAGE_PATH = process.env.LOCAL_STORAGE_PATH || '/data/storage';

    // S3
    this.S3_BUCKET = process.env.S3_BUCKET || '';
    this.S3_REGION = process.env.S3_REGION || 'us-east-1';
    this.S3_ACCESS_KEY_ID = process.env.S3_ACCESS_KEY_ID || '';
    this.S3_SECRET_ACCESS_KEY = process.env.S3_SECRET_ACCESS_KEY || '';
    this.S3_ENDPOINT = process.env.S3_ENDPOINT || '';

    // Google Cloud Storage
    this.GCS_BUCKET = process.env.GCS_BUCKET || '';
    this.GCS_PROJECT_ID = process.env.GCS_PROJECT_ID || '';
    this.GCS_CREDENTIALS_PATH = process.env.GCS_CREDENTIALS_PATH || '';

    // Azure
    this.AZURE_STORAGE_ACCOUNT = process.env.AZURE_STORAGE_ACCOUNT || '';
    this.AZURE_STORAGE_KEY = process.env.AZURE_STORAGE_KEY || '';
    this.AZURE_CONTAINER = process.env.AZURE_CONTAINER || '';

    // API
    this.PORT = parseInt(process.env.PORT || '3001');
    this.API_KEY = process.env.STORAGE_API_KEY || '';
    this.CORS_ENABLED = process.env.CORS_ENABLED !== 'false';

    // File Upload
    this.MAX_FILE_SIZE_MB = parseInt(process.env.MAX_FILE_SIZE_MB || '100');
    this.ALLOWED_MIME_TYPES = (process.env.ALLOWED_MIME_TYPES || 'image/*,video/*,application/pdf').split(',');
    this.TEMP_UPLOAD_PATH = process.env.TEMP_UPLOAD_PATH || '/tmp/uploads';

    this.logConfiguration();
  }

  /**
   * Get storage backend config based on selected backend
   */
  getStorageBackendConfig(): any {
    switch (this.STORAGE_BACKEND) {
      case 's3':
        return {
          bucket: this.S3_BUCKET,
          region: this.S3_REGION,
          accessKeyId: this.S3_ACCESS_KEY_ID,
          secretAccessKey: this.S3_SECRET_ACCESS_KEY,
          endpoint: this.S3_ENDPOINT,
        };

      case 'gcs':
        return {
          bucket: this.GCS_BUCKET,
          projectId: this.GCS_PROJECT_ID,
          credentialsPath: this.GCS_CREDENTIALS_PATH,
        };

      case 'azure':
        return {
          account: this.AZURE_STORAGE_ACCOUNT,
          key: this.AZURE_STORAGE_KEY,
          container: this.AZURE_CONTAINER,
        };

      case 'local':
      default:
        return {
          path: this.LOCAL_STORAGE_PATH,
        };
    }
  }

  /**
   * Check if API key authentication is enabled
   */
  isApiKeyEnabled(): boolean {
    return !!this.API_KEY;
  }

  /**
   * Log loaded configuration (without sensitive data)
   */
  private logConfiguration() {
    this.logger.log('📋 Configuration loaded:');
    this.logger.log(`  Storage Backend: ${this.STORAGE_BACKEND}`);
    this.logger.log(`  Port: ${this.PORT}`);
    this.logger.log(`  CORS: ${this.CORS_ENABLED ? '✅' : '❌'}`);
    this.logger.log(`  API Key Auth: ${this.isApiKeyEnabled() ? '✅' : '❌ (open access)'}`);
    this.logger.log(`  Max File Size: ${this.MAX_FILE_SIZE_MB}MB`);
    this.logger.log(`  Allowed Types: ${this.ALLOWED_MIME_TYPES.join(', ')}`);

    // Backend-specific configuration
    switch (this.STORAGE_BACKEND) {
      case 's3':
        this.logger.log(`  S3 Bucket: ${this.S3_BUCKET}`);
        this.logger.log(`  S3 Region: ${this.S3_REGION}`);
        this.logger.log(`  S3 Custom Endpoint: ${this.S3_ENDPOINT || 'Default AWS'}`);
        break;

      case 'gcs':
        this.logger.log(`  GCS Bucket: ${this.GCS_BUCKET}`);
        this.logger.log(`  GCS Project: ${this.GCS_PROJECT_ID}`);
        break;

      case 'azure':
        this.logger.log(`  Azure Account: ${this.AZURE_STORAGE_ACCOUNT}`);
        this.logger.log(`  Azure Container: ${this.AZURE_CONTAINER}`);
        break;

      case 'local':
      default:
        this.logger.log(`  Local Path: ${this.LOCAL_STORAGE_PATH}`);
        break;
    }
  }

  /**
   * Validate required environment variables
   */
  validateConfig(): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    // Validate based on storage backend
    switch (this.STORAGE_BACKEND) {
      case 's3':
        if (!this.S3_BUCKET) errors.push('❌ S3_BUCKET is required for S3 backend');
        if (!this.S3_ACCESS_KEY_ID) errors.push('❌ S3_ACCESS_KEY_ID is required for S3 backend');
        if (!this.S3_SECRET_ACCESS_KEY) errors.push('❌ S3_SECRET_ACCESS_KEY is required for S3 backend');
        break;

      case 'gcs':
        if (!this.GCS_BUCKET) errors.push('❌ GCS_BUCKET is required for GCS backend');
        if (!this.GCS_PROJECT_ID) errors.push('❌ GCS_PROJECT_ID is required for GCS backend');
        if (!this.GCS_CREDENTIALS_PATH) errors.push('❌ GCS_CREDENTIALS_PATH is required for GCS backend');
        break;

      case 'azure':
        if (!this.AZURE_STORAGE_ACCOUNT) errors.push('❌ AZURE_STORAGE_ACCOUNT is required for Azure backend');
        if (!this.AZURE_STORAGE_KEY) errors.push('❌ AZURE_STORAGE_KEY is required for Azure backend');
        if (!this.AZURE_CONTAINER) errors.push('❌ AZURE_CONTAINER is required for Azure backend');
        break;

      case 'local':
        if (!this.LOCAL_STORAGE_PATH) errors.push('❌ LOCAL_STORAGE_PATH is required for local backend');
        break;

      default:
        errors.push(`❌ Invalid STORAGE_BACKEND: ${this.STORAGE_BACKEND}`);
    }

    if (!this.isApiKeyEnabled()) {
      errors.push('⚠️  No API key configured - storage API is open to all');
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
