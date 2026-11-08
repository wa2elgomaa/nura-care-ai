import { Injectable, Logger } from '@nestjs/common';

/**
 * Activity Classifier Service
 *
 * Simple rule-based activity classification from bounding box movement
 * Week 5: Student behavioral analytics
 */
@Injectable()
export class ActivityClassifierService {
  private readonly logger = new Logger(ActivityClassifierService.name);

  // Track previous bounding boxes per person/camera
  private previousBboxes: Map<string, any> = new Map();

  constructor() {
    this.logger.log('✅ Activity Classifier initialized (rule-based)');
  }

  /**
   * Classify activity based on bounding box movement and shape
   *
   * Activities: playing, running, sitting, standing, eating, sleeping, reading, building, interacting, alone, other
   */
  classifyActivity(
    person_id: string,
    camera_id: string,
    current_bbox: { x1: number; y1: number; x2: number; y2: number },
    context?: {
      zone?: string;
      time_of_day?: number;
    }
  ): { activity: string; confidence: number } {
    const key = `${person_id}_${camera_id}`;
    const previous_bbox = this.previousBboxes.get(key);

    // Store current bbox for next comparison
    this.previousBboxes.set(key, { ...current_bbox, timestamp: Date.now() });

    // If no previous bbox, can't determine movement
    if (!previous_bbox) {
      return this.classifyByContext(current_bbox, context);
    }

    // Calculate movement and shape metrics
    const movement = this.calculateMovement(current_bbox, previous_bbox);
    const aspectRatio = this.calculateAspectRatio(current_bbox);
    const timeDelta = Date.now() - previous_bbox.timestamp;

    // Normalize movement by time (pixels per second)
    const movementSpeed = timeDelta > 0 ? (movement / timeDelta) * 1000 : 0;

    // Rule-based classification
    return this.classifyByRules(movementSpeed, aspectRatio, context);
  }

  /**
   * Rule-based classification from movement and shape
   */
  private classifyByRules(
    movementSpeed: number,
    aspectRatio: number,
    context?: { zone?: string; time_of_day?: number }
  ): { activity: string; confidence: number } {
    const zone = context?.zone || 'unknown';
    const hour = context?.time_of_day || new Date().getHours();

    // Context-based overrides
    if (zone === 'cafeteria' && hour >= 11 && hour <= 13) {
      return { activity: 'eating', confidence: 0.75 };
    }

    if (zone === 'quiet' || (hour >= 13 && hour <= 14)) {
      if (movementSpeed < 5) {
        return { activity: 'sleeping', confidence: 0.70 };
      }
    }

    // Movement-based classification
    if (movementSpeed > 100) {
      return { activity: 'running', confidence: 0.80 };
    }

    if (movementSpeed > 30) {
      return { activity: 'playing', confidence: 0.75 };
    }

    if (movementSpeed > 10) {
      return { activity: 'interacting', confidence: 0.65 };
    }

    // Shape-based classification (when stationary)
    if (movementSpeed < 10) {
      if (aspectRatio > 1.8) {
        return { activity: 'standing', confidence: 0.70 };
      }

      if (aspectRatio < 1.3) {
        return { activity: 'sitting', confidence: 0.75 };
      }

      // Medium aspect ratio, stationary
      if (zone === 'classroom') {
        return { activity: 'reading', confidence: 0.60 };
      }

      return { activity: 'sitting', confidence: 0.65 };
    }

    // Default
    return { activity: 'other', confidence: 0.50 };
  }

  /**
   * Classify by context when no movement data available
   */
  private classifyByContext(
    bbox: any,
    context?: { zone?: string; time_of_day?: number }
  ): { activity: string; confidence: number } {
    const zone = context?.zone || 'unknown';
    const hour = context?.time_of_day || new Date().getHours();
    const aspectRatio = this.calculateAspectRatio(bbox);

    // Context-based defaults
    if (zone === 'cafeteria' && hour >= 11 && hour <= 13) {
      return { activity: 'eating', confidence: 0.60 };
    }

    if (zone === 'playground' || zone === 'outdoor') {
      return { activity: 'playing', confidence: 0.65 };
    }

    if (zone === 'quiet') {
      return { activity: 'sleeping', confidence: 0.60 };
    }

    // Shape-based guess
    if (aspectRatio > 1.8) {
      return { activity: 'standing', confidence: 0.55 };
    }

    if (aspectRatio < 1.3) {
      return { activity: 'sitting', confidence: 0.60 };
    }

    return { activity: 'other', confidence: 0.40 };
  }

  /**
   * Calculate movement between two bounding boxes (Euclidean distance of centers)
   */
  private calculateMovement(
    current: { x1: number; y1: number; x2: number; y2: number },
    previous: { x1: number; y1: number; x2: number; y2: number }
  ): number {
    const currentCenterX = (current.x1 + current.x2) / 2;
    const currentCenterY = (current.y1 + current.y2) / 2;
    const previousCenterX = (previous.x1 + previous.x2) / 2;
    const previousCenterY = (previous.y1 + previous.y2) / 2;

    const dx = currentCenterX - previousCenterX;
    const dy = currentCenterY - previousCenterY;

    return Math.sqrt(dx * dx + dy * dy);
  }

  /**
   * Calculate aspect ratio (height / width)
   */
  private calculateAspectRatio(bbox: { x1: number; y1: number; x2: number; y2: number }): number {
    const height = bbox.y2 - bbox.y1;
    const width = bbox.x2 - bbox.x1;

    return width > 0 ? height / width : 1.0;
  }

  /**
   * Clean up old bounding boxes (older than 30 seconds)
   */
  cleanup() {
    const now = Date.now();
    const maxAge = 30000; // 30 seconds

    for (const [key, bbox] of this.previousBboxes.entries()) {
      if (now - bbox.timestamp > maxAge) {
        this.previousBboxes.delete(key);
      }
    }
  }
}
