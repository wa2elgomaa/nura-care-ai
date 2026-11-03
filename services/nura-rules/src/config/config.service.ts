import { Injectable } from '@nestjs/common';

@Injectable()
export class ConfigService {
  get databaseUrl(): string {
    return process.env.DATABASE_URL || 'postgresql://nura:password@postgres:5432/nura';
  }

  get natsUrl(): string {
    return process.env.NATS_URL || 'nats://nats:4222';
  }

  get ragServiceUrl(): string {
    return process.env.RAG_SERVICE_URL || 'http://nura-rag:3002';
  }

  get vlmServiceUrl(): string {
    return process.env.VLM_SERVICE_URL || 'http://nura-vlm:8001';
  }

  get siteId(): string {
    return process.env.SITE_ID || 'dev-site-001';
  }

  get supervisionThresholdSeconds(): number {
    return parseInt(process.env.SUPERVISION_THRESHOLD_SECONDS || '30', 10);
  }
}
