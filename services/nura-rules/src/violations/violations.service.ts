import { Injectable, Logger, OnModuleInit } from '@nestjs/common';
import { Pool } from 'pg';
import { ConfigService } from '../config/config.service.js';

export interface DetectionEvent {
  camera_id: string;
  timestamp: string;
  event_type: 'no_adults_detected' | 'fall_detected' | 'capacity_exceeded' | 'restricted_area_access';
  persons_detected?: number;
  adults_detected?: number;
  children_detected?: number;
  confidence?: number;
  metadata?: Record<string, any>;
}

export interface VLMAnalysis {
  analysis: string;
  adults_detected?: boolean;
  children_count?: number;
  safety_concern?: boolean;
  confidence?: number;
}

export interface RuleMatch {
  rule_id: string;
  title: string;
  description: string;
  clause: string;
  source: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  category: string;
  similarity: number;
}

export interface ViolationAlert {
  event_id: string;
  rule_id: string;
  camera_id: string;
  site_id: string;
  timestamp: Date;
  severity: string;
  title: string;
  description: string;
  context: string;
  evidence_clip_path?: string;
  rule_source: string;
}

/**
 * Violations Service
 * Core rules engine: orchestrates detection → VLM → RAG → violation alerts
 * Spec: specs/024-rules-engine-violation/spec.md FR-001 through FR-007
 */
@Injectable()
export class ViolationsService implements OnModuleInit {
  private readonly logger = new Logger(ViolationsService.name);
  private pool!: Pool;
  private eventTracker: Map<string, DetectionEvent & { started_at: Date }> = new Map();

  constructor(private readonly config: ConfigService) {}

  async onModuleInit() {
    // Initialize database connection
    this.pool = new Pool({
      connectionString: this.config.databaseUrl,
      max: 10,
    });

    this.logger.log('✓ Violations service initialized');
  }

  /**
   * Main pipeline: Process detection event through full workflow
   * FR-001, FR-002, FR-003, FR-004, FR-005, FR-006
   */
  async processDetectionEvent(
    event: DetectionEvent,
    vlmAnalysis?: VLMAnalysis,
  ): Promise<ViolationAlert | null> {
    const startTime = Date.now();

    try {
      this.logger.log(
        `Processing detection: ${event.event_type} at ${event.camera_id}`,
      );

      // Step 1: Track event duration (FR-003: threshold evaluation)
      const eventKey = `${event.camera_id}_${event.event_type}`;
      const tracked = this.eventTracker.get(eventKey);

      if (!tracked) {
        // First occurrence - start tracking
        this.eventTracker.set(eventKey, {
          ...event,
          started_at: new Date(),
        });

        this.logger.debug(
          `Started tracking event: ${eventKey}`,
        );

        // Check again after threshold period
        setTimeout(() => {
          this.checkThreshold(eventKey);
        }, this.config.supervisionThresholdSeconds * 1000);

        return null; // Don't alert yet, waiting for threshold
      }

      // Step 2: Check if threshold met
      const durationSeconds =
        (Date.now() - tracked.started_at.getTime()) / 1000;

      if (durationSeconds < this.config.supervisionThresholdSeconds) {
        this.logger.debug(
          `Event ${eventKey} duration ${durationSeconds}s < threshold ${this.config.supervisionThresholdSeconds}s`,
        );
        return null; // Threshold not met yet
      }

      // Step 3: Query RAG for matching rules (FR-002)
      const context = this.buildEventContext(event, vlmAnalysis);
      const ruleMatches = await this.queryRAG(context, event.event_type);

      if (!ruleMatches || ruleMatches.length === 0) {
        this.logger.warn('No matching rules found for event');
        this.eventTracker.delete(eventKey); // Clear tracker
        return null;
      }

      const topMatch = ruleMatches[0];

      this.logger.log(
        `Rule matched: ${topMatch.rule_id} (similarity: ${topMatch.similarity})`,
      );

      // Step 4: Generate violation alert (FR-004)
      const violation = await this.createViolation(
        event,
        topMatch,
        context,
        durationSeconds,
      );

      // Step 5: Store in database (FR-006)
      await this.storeViolation(violation);

      // Clear tracker
      this.eventTracker.delete(eventKey);

      const totalLatency = Date.now() - startTime;
      this.logger.log(
        `✓ Violation alert generated in ${totalLatency}ms (target: <10000ms)`,
      );

      if (totalLatency > 10000) {
        this.logger.warn(`⚠ Exceeded 10s latency target: ${totalLatency}ms`);
      }

      return violation;
    } catch (error) {
      this.logger.error('Failed to process detection event:', error);
      throw error;
    }
  }

  /**
   * Check if tracked event still meets conditions after threshold period
   */
  private async checkThreshold(eventKey: string) {
    const tracked = this.eventTracker.get(eventKey);
    if (!tracked) {
      return; // Event already processed or cleared
    }

    const durationSeconds =
      (Date.now() - tracked.started_at.getTime()) / 1000;

    if (durationSeconds >= this.config.supervisionThresholdSeconds) {
      this.logger.log(
        `Threshold met for ${eventKey} (${durationSeconds}s), processing violation...`,
      );

      // Trigger violation processing
      await this.processDetectionEvent(tracked);
    } else {
      // Condition resolved before threshold
      this.logger.debug(`Event ${eventKey} resolved before threshold`);
      this.eventTracker.delete(eventKey);
    }
  }

  /**
   * Build context string for RAG query
   */
  private buildEventContext(
    event: DetectionEvent,
    vlmAnalysis?: VLMAnalysis,
  ): string {
    let context = '';

    if (event.event_type === 'no_adults_detected') {
      context = `${event.children_detected || 'Multiple'} children visible, no adult present`;

      if (vlmAnalysis?.analysis) {
        context += `. VLM analysis: ${vlmAnalysis.analysis}`;
      }
    } else if (event.event_type === 'fall_detected') {
      context = 'Person detected in horizontal pose (potential fall)';
    } else if (event.event_type === 'capacity_exceeded') {
      context = `${event.persons_detected} persons in room (over capacity)`;
    } else if (event.event_type === 'restricted_area_access') {
      context = 'Child detected in restricted area';
    }

    return context;
  }

  /**
   * Query RAG service for matching rules (FR-002)
   */
  private async queryRAG(
    context: string,
    eventType: string,
  ): Promise<RuleMatch[]> {
    try {
      // Map event type to rule category
      const categoryMap: Record<string, string> = {
        no_adults_detected: 'supervision',
        fall_detected: 'safety',
        capacity_exceeded: 'capacity',
        restricted_area_access: 'restricted_area',
      };

      const category = categoryMap[eventType];

      const response = await fetch(`${this.config.ragServiceUrl}/match`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          event_context: context,
          category,
          top_k: this.config.RAG_TOP_K,
          similarity_threshold: this.config.RAG_SIMILARITY_THRESHOLD,
        }),
      });

      if (!response.ok) {
        throw new Error(`RAG service error: ${response.statusText}`);
      }

      const data = await response.json() as { matches?: RuleMatch[] };
      return data.matches || [];
    } catch (error) {
      this.logger.error('Failed to query RAG service:', error);
      return [];
    }
  }

  /**
   * Create violation alert object (FR-004)
   */
  private async createViolation(
    event: DetectionEvent,
    rule: RuleMatch,
    context: string,
    durationSeconds: number,
  ): Promise<ViolationAlert> {
    const eventId = `EVT-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

    // Evidence clip path (FR-004: evidence management)
    const evidenceClipPath = this.generateEvidenceClipPath(
      event.camera_id,
      new Date(event.timestamp),
    );

    return {
      event_id: eventId,
      rule_id: rule.rule_id,
      camera_id: event.camera_id,
      site_id: this.config.siteId,
      timestamp: new Date(event.timestamp),
      severity: rule.severity,
      title: rule.title,
      description: `${rule.description}. Duration: ${Math.round(durationSeconds)}s`,
      context,
      evidence_clip_path: evidenceClipPath,
      rule_source: rule.source,
    };
  }

  /**
   * Generate evidence clip path (FR-004)
   */
  private generateEvidenceClipPath(cameraId: string, timestamp: Date): string {
    const date = timestamp.toISOString().split('T')[0];
    const time = timestamp.toISOString().split('T')[1].replace(/:/g, '-').split('.')[0];
    return `/evidence/${date}/${cameraId}/${time}.mp4`;
  }

  /**
   * Store violation in database (FR-006)
   */
  private async storeViolation(violation: ViolationAlert): Promise<void> {
    const query = `
      INSERT INTO violation_events (
        event_id, rule_id, camera_id, site_id, timestamp,
        context, evidence_clip_path, severity, status, metadata
      )
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
    `;

    const metadata = {
      title: violation.title,
      description: violation.description,
      rule_source: violation.rule_source,
    };

    await this.pool.query(query, [
      violation.event_id,
      violation.rule_id,
      violation.camera_id,
      violation.site_id,
      violation.timestamp,
      violation.context,
      violation.evidence_clip_path,
      violation.severity,
      'open',
      JSON.stringify(metadata),
    ]);

    this.logger.log(`Stored violation: ${violation.event_id}`);
  }

  /**
   * Get recent violations (for dashboard)
   */
  async getRecentViolations(limit: number = 50): Promise<any[]> {
    const query = `
      SELECT
        event_id,
        rule_id,
        camera_id,
        timestamp,
        context,
        evidence_clip_path,
        severity,
        status,
        metadata,
        created_at
      FROM violation_events
      ORDER BY timestamp DESC
      LIMIT $1
    `;

    const result = await this.pool.query(query, [limit]);
    return result.rows;
  }

  /**
   * Acknowledge violation
   */
  async acknowledgeViolation(
    eventId: string,
    acknowledgedBy: string,
  ): Promise<void> {
    const query = `
      UPDATE violation_events
      SET status = 'acknowledged',
          acknowledged_by = $1,
          acknowledged_at = NOW()
      WHERE event_id = $2
    `;

    await this.pool.query(query, [acknowledgedBy, eventId]);
    this.logger.log(`Violation acknowledged: ${eventId} by ${acknowledgedBy}`);
  }
}
