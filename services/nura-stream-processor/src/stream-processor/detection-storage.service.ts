import { Injectable, Logger } from '@nestjs/common';
import { Pool } from 'pg';
import { ConfigService } from '../config/config.service';

/**
 * Detection Storage Service
 *
 * Stores person detection events to database for analytics
 * Week 5: Student behavioral analytics
 */
@Injectable()
export class DetectionStorageService {
  private readonly logger = new Logger(DetectionStorageService.name);
  private pool: Pool;

  constructor(private readonly config: ConfigService) {
    // PostgreSQL connection pool from centralized config
    this.pool = new Pool(this.config.getDatabaseConfig());

    this.pool.on('error', (err) => {
      this.logger.error('PostgreSQL pool error:', err);
    });

    this.logger.log('✅ Detection Storage Service initialized');
  }

  /**
   * Save detection event to person_detections table
   */
  async saveDetection(data: {
    person_id: string;
    camera_id: string;
    zone_name?: string;
    activity?: string;
    activity_confidence?: number;
    confidence: number;
    bbox?: any;
    frame_url?: string;
  }): Promise<void> {
    try {
      await this.pool.query(
        `INSERT INTO person_detections
         (person_id, camera_id, zone_name, activity, activity_confidence, confidence, bbox, frame_url, detected_at)
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW())`,
        [
          data.person_id,
          data.camera_id,
          data.zone_name || null,
          data.activity || null,
          data.activity_confidence || null,
          data.confidence,
          data.bbox ? JSON.stringify(data.bbox) : null,
          data.frame_url || null,
        ]
      );

      this.logger.debug(`✅ Saved detection: ${data.person_id} @ ${data.camera_id} (${data.activity || 'unknown'})`);
    } catch (error) {
      this.logger.error(`Failed to save detection: ${error.message}`, error.stack);
      // Don't throw - we don't want to stop processing if DB save fails
    }
  }

  /**
   * Update location cache in Redis
   */
  async updateLocationCache(data: {
    person_id: string;
    camera_id: string;
    zone_name?: string;
    activity?: string;
    confidence: number;
  }): Promise<void> {
    try {
      // This would update Redis cache for real-time location tracking
      // For now, we'll implement this later when Redis client is added
      this.logger.debug(`Location cache update: ${data.person_id} @ ${data.camera_id}`);
    } catch (error) {
      this.logger.error(`Failed to update location cache: ${error.message}`);
    }
  }

  /**
   * Get zone name from camera ID
   * Maps camera to zone/area in the facility
   */
  getZoneName(camera_id: string): string {
    // Camera to zone mapping
    const zoneMap: { [key: string]: string } = {
      'classroom_1': 'classroom',
      'classroom_2': 'classroom',
      'classroom_3': 'classroom',
      'playground': 'outdoor',
      'cafeteria': 'cafeteria',
      'entrance': 'entrance',
      'hallway': 'hallway',
      'quiet_room': 'quiet',
      'kitchen': 'kitchen',
      'bathroom_boys_1f': 'bathroom',
      'bathroom_girls_1f': 'bathroom',
      'storage_main': 'storage',
    };

    return zoneMap[camera_id] || 'unknown';
  }

  /**
   * Health check - verify database connection
   */
  async healthCheck(): Promise<boolean> {
    try {
      const result = await this.pool.query('SELECT 1');
      return result.rows.length > 0;
    } catch (error) {
      this.logger.error(`Database health check failed: ${error.message}`);
      return false;
    }
  }

  /**
   * Cleanup on service shutdown
   */
  async onModuleDestroy() {
    await this.pool.end();
    this.logger.log('Database pool closed');
  }
}
