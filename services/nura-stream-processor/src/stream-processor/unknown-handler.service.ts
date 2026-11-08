import { Injectable, Logger } from '@nestjs/common';
import { Pool } from 'pg';
import { ConfigService } from '../config/config.service';

/**
 * Unknown Person Handler Service
 *
 * Auto-creates "Unknown Person N" entries for unidentified individuals
 * Week 5: Track potential unenrolled students
 */
@Injectable()
export class UnknownHandlerService {
  private readonly logger = new Logger(UnknownHandlerService.name);
  private pool: Pool;

  constructor(private readonly config: ConfigService) {
    // PostgreSQL connection pool from centralized config
    this.pool = new Pool(this.config.getDatabaseConfig());

    this.logger.log('✅ Unknown Handler Service initialized');
  }

  /**
   * Find or create unknown person entry
   * Returns unknown_id (e.g., 'unknown_001')
   */
  async findOrCreateUnknown(face_embedding: number[]): Promise<string> {
    try {
      // First, check if this face matches an existing unknown
      const existing = await this.findSimilarUnknown(face_embedding);

      if (existing && existing.similarity > 0.7) {
        // Same unknown person - update last_seen
        await this.updateLastSeen(existing.unknown_id);
        this.logger.debug(`✅ Matched existing unknown: ${existing.unknown_id} (similarity: ${existing.similarity.toFixed(2)})`);
        return existing.unknown_id;
      }

      // New unknown - create entry
      const unknown_id = await this.createNewUnknown(face_embedding);
      this.logger.log(`🆕 Created new unknown person: ${unknown_id}`);

      return unknown_id;

    } catch (error) {
      this.logger.error(`Failed to find/create unknown: ${error.message}`);
      // Return generic unknown ID if database fails
      return 'unknown_temp';
    }
  }

  /**
   * Find similar unknown by face embedding (vector similarity)
   */
  private async findSimilarUnknown(face_embedding: number[]): Promise<{ unknown_id: string; similarity: number } | null> {
    try {
      const result = await this.pool.query(
        `SELECT
           unknown_id,
           1 - (face_embedding <=> $1::vector) as similarity
         FROM unknown_persons
         WHERE active = true
           AND linked_to_person_id IS NULL
         ORDER BY face_embedding <=> $1::vector
         LIMIT 1`,
        [JSON.stringify(face_embedding)]
      );

      if (result.rows.length > 0) {
        return {
          unknown_id: result.rows[0].unknown_id,
          similarity: parseFloat(result.rows[0].similarity),
        };
      }

      return null;
    } catch (error) {
      this.logger.error(`Failed to find similar unknown: ${error.message}`);
      return null;
    }
  }

  /**
   * Create new unknown person entry
   */
  private async createNewUnknown(face_embedding: number[]): Promise<string> {
    try {
      // Get next unknown ID using database function
      const idResult = await this.pool.query('SELECT get_next_unknown_id() as unknown_id');
      const unknown_id = idResult.rows[0]?.unknown_id || 'unknown_001';

      // Insert new unknown
      await this.pool.query(
        `INSERT INTO unknown_persons (unknown_id, face_embedding, first_seen, last_seen, detection_count)
         VALUES ($1, $2, NOW(), NOW(), 1)`,
        [unknown_id, JSON.stringify(face_embedding)]
      );

      return unknown_id;
    } catch (error) {
      this.logger.error(`Failed to create new unknown: ${error.message}`);
      // Fallback to timestamp-based ID
      return `unknown_${Date.now()}`;
    }
  }

  /**
   * Update last_seen timestamp for existing unknown
   */
  private async updateLastSeen(unknown_id: string): Promise<void> {
    try {
      await this.pool.query(
        `UPDATE unknown_persons
         SET last_seen = NOW(),
             detection_count = detection_count + 1
         WHERE unknown_id = $1`,
        [unknown_id]
      );
    } catch (error) {
      this.logger.error(`Failed to update last_seen for ${unknown_id}: ${error.message}`);
    }
  }

  /**
   * Check if unknown has been linked to a real person
   */
  async isLinked(unknown_id: string): Promise<string | null> {
    try {
      const result = await this.pool.query(
        'SELECT linked_to_person_id FROM unknown_persons WHERE unknown_id = $1',
        [unknown_id]
      );

      if (result.rows.length > 0) {
        return result.rows[0].linked_to_person_id;
      }

      return null;
    } catch (error) {
      this.logger.error(`Failed to check link status: ${error.message}`);
      return null;
    }
  }

  async onModuleDestroy() {
    await this.pool.end();
  }
}
