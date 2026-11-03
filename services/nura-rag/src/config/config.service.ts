import { Injectable } from '@nestjs/common';

@Injectable()
export class ConfigService {
  get databaseUrl(): string {
    return process.env.DATABASE_URL || 'postgresql://nura:password@postgres:5432/nura';
  }

  get embeddingModel(): string {
    return process.env.EMBEDDING_MODEL || 'Xenova/all-MiniLM-L6-v2';
  }

  get embeddingDimensions(): number {
    return 384; // all-MiniLM-L6-v2
  }

  get similarityThreshold(): number {
    return parseFloat(process.env.SIMILARITY_THRESHOLD || '0.7');
  }

  get siteId(): string {
    return process.env.SITE_ID || 'dev-site-001';
  }
}
