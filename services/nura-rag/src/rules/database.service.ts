import { Injectable, OnModuleInit, OnModuleDestroy, Logger } from '@nestjs/common';
import { Pool, PoolClient } from 'pg';
import { ConfigService } from '../config/config.service.js';

/**
 * Database Service
 * Manages Postgres connection pool with pgvector support
 */
@Injectable()
export class DatabaseService implements OnModuleInit, OnModuleDestroy {
  private readonly logger = new Logger(DatabaseService.name);
  private pool: Pool | null = null;

  constructor(private readonly config: ConfigService) {}

  async onModuleInit() {
    this.logger.log('Connecting to Postgres with pgvector...');

    try {
      this.pool = new Pool({
        connectionString: this.config.databaseUrl,
        max: 20,
        idleTimeoutMillis: 30000,
        connectionTimeoutMillis: 2000,
      });

      // Test connection
      const client = await this.pool.connect();
      const result = await client.query('SELECT 1 as connected');
      client.release();

      this.logger.log('✓ Postgres connected successfully');
      this.logger.debug(`Connection pool size: ${this.pool.totalCount}`);
    } catch (error) {
      this.logger.error('✗ Failed to connect to Postgres:', error);
      throw error;
    }
  }

  async onModuleDestroy() {
    if (this.pool) {
      await this.pool.end();
      this.logger.log('Postgres connection pool closed');
    }
  }

  /**
   * Get a client from the connection pool
   */
  async getClient(): Promise<PoolClient> {
    if (!this.pool) {
      throw new Error('Database pool not initialized');
    }
    return this.pool.connect();
  }

  /**
   * Execute a query
   */
  async query<T = any>(text: string, params?: any[]): Promise<T[]> {
    if (!this.pool) {
      throw new Error('Database pool not initialized');
    }

    const start = Date.now();
    const result = await this.pool.query(text, params);
    const duration = Date.now() - start;

    this.logger.debug(`Query executed in ${duration}ms`);

    return result.rows;
  }
}
