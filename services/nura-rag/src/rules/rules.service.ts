import { Injectable, Logger } from '@nestjs/common';
import { DatabaseService } from './database.service.js';
import { EmbeddingsService } from '../embeddings/embeddings.service.js';
import { ConfigService } from '../config/config.service.js';

export interface Rule {
  id: number;
  rule_id: string;
  title: string;
  description: string;
  clause: string;
  source: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  category: string;
  enabled: boolean;
  metadata?: Record<string, any>;
  created_at?: Date;
  updated_at?: Date;
}

export interface RuleMatch extends Rule {
  similarity: number;
}

export interface MatchRequest {
  event_context: string;
  category?: string;
  top_k?: number;
  similarity_threshold?: number;
}

export interface MatchResponse {
  matches: RuleMatch[];
  query_time_ms: number;
}

/**
 * Rules Service
 * Core RAG functionality: rule matching via semantic similarity (pgvector)
 * Spec: FR-001, FR-002, FR-003, FR-004
 */
@Injectable()
export class RulesService {
  private readonly logger = new Logger(RulesService.name);

  constructor(
    private readonly db: DatabaseService,
    private readonly embeddings: EmbeddingsService,
    private readonly config: ConfigService,
  ) {}

  /**
   * Match event context to rules using semantic similarity
   * FR-001: POST /match endpoint
   */
  async matchRules(request: MatchRequest): Promise<MatchResponse> {
    const start = Date.now();

    const {
      event_context,
      category,
      top_k = 5,
      similarity_threshold = this.config.similarityThreshold,
    } = request;

    try {
      // Generate embedding for event context
      this.logger.debug(`Generating embedding for: "${event_context.substring(0, 50)}..."`);
      const queryEmbedding = await this.embeddings.generateEmbedding(event_context);

      // Format embedding as pgvector string
      const embeddingStr = `[${queryEmbedding.join(',')}]`;

      // Build query with optional category filter
      let query = `
        SELECT
          id,
          rule_id,
          title,
          description,
          clause,
          source,
          severity,
          category,
          enabled,
          metadata,
          1 - (embedding <=> $1::vector) AS similarity
        FROM rules
        WHERE enabled = true
          AND 1 - (embedding <=> $1::vector) >= $2
      `;

      const params: any[] = [embeddingStr, similarity_threshold];

      if (category) {
        query += ` AND category = $3`;
        params.push(category);
      }

      query += `
        ORDER BY embedding <=> $1::vector
        LIMIT $${params.length + 1}
      `;
      params.push(top_k);

      // Execute query
      this.logger.debug('Executing pgvector similarity search...');
      const rows = await this.db.query<RuleMatch>(query, params);

      const queryTime = Date.now() - start;

      this.logger.log(
        `Found ${rows.length} matching rules in ${queryTime}ms (threshold: ${similarity_threshold})`,
      );

      return {
        matches: rows,
        query_time_ms: queryTime,
      };
    } catch (error) {
      this.logger.error('Rule matching failed:', error);
      throw error;
    }
  }

  /**
   * Get all rules with optional filters
   */
  async getRules(filters?: {
    category?: string;
    severity?: string;
    enabled?: boolean;
  }): Promise<Rule[]> {
    let query = 'SELECT * FROM rules WHERE 1=1';
    const params: any[] = [];
    let paramIndex = 1;

    if (filters?.category) {
      query += ` AND category = $${paramIndex++}`;
      params.push(filters.category);
    }

    if (filters?.severity) {
      query += ` AND severity = $${paramIndex++}`;
      params.push(filters.severity);
    }

    if (filters?.enabled !== undefined) {
      query += ` AND enabled = $${paramIndex++}`;
      params.push(filters.enabled);
    }

    query += ' ORDER BY severity DESC, title ASC';

    return this.db.query<Rule>(query, params);
  }

  /**
   * Get rule by ID
   */
  async getRule(ruleId: string): Promise<Rule | null> {
    const rows = await this.db.query<Rule>(
      'SELECT * FROM rules WHERE rule_id = $1',
      [ruleId],
    );

    return rows[0] || null;
  }

  /**
   * Create new rule with embedding
   */
  async createRule(
    rule: Omit<Rule, 'id' | 'created_at' | 'updated_at'>,
  ): Promise<Rule> {
    // Generate embedding for rule text
    const ruleText = `${rule.title}. ${rule.description}. ${rule.clause}`;
    const embedding = await this.embeddings.generateEmbedding(ruleText);
    const embeddingStr = `[${embedding.join(',')}]`;

    const query = `
      INSERT INTO rules (
        rule_id, title, description, clause, source,
        severity, category, embedding, metadata, enabled
      )
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8::vector, $9, $10)
      RETURNING *
    `;

    const rows = await this.db.query<Rule>(query, [
      rule.rule_id,
      rule.title,
      rule.description,
      rule.clause,
      rule.source,
      rule.severity,
      rule.category,
      embeddingStr,
      JSON.stringify(rule.metadata || {}),
      rule.enabled ?? true,
    ]);

    this.logger.log(`Created rule: ${rule.rule_id}`);

    return rows[0];
  }

  /**
   * Update rule (regenerates embedding if text changed)
   */
  async updateRule(
    ruleId: string,
    updates: Partial<Omit<Rule, 'id' | 'created_at' | 'updated_at'>>,
  ): Promise<Rule> {
    const existing = await this.getRule(ruleId);
    if (!existing) {
      throw new Error(`Rule not found: ${ruleId}`);
    }

    // Check if text fields changed (need to regenerate embedding)
    const textChanged =
      updates.title !== undefined ||
      updates.description !== undefined ||
      updates.clause !== undefined;

    let embeddingStr: string | undefined;

    if (textChanged) {
      const ruleText = `${updates.title || existing.title}. ${updates.description || existing.description}. ${updates.clause || existing.clause}`;
      const embedding = await this.embeddings.generateEmbedding(ruleText);
      embeddingStr = `[${embedding.join(',')}]`;
    }

    // Build dynamic update query
    const setClauses: string[] = [];
    const params: any[] = [];
    let paramIndex = 1;

    if (updates.title) {
      setClauses.push(`title = $${paramIndex++}`);
      params.push(updates.title);
    }
    if (updates.description) {
      setClauses.push(`description = $${paramIndex++}`);
      params.push(updates.description);
    }
    if (updates.clause) {
      setClauses.push(`clause = $${paramIndex++}`);
      params.push(updates.clause);
    }
    if (updates.source) {
      setClauses.push(`source = $${paramIndex++}`);
      params.push(updates.source);
    }
    if (updates.severity) {
      setClauses.push(`severity = $${paramIndex++}`);
      params.push(updates.severity);
    }
    if (updates.category) {
      setClauses.push(`category = $${paramIndex++}`);
      params.push(updates.category);
    }
    if (updates.enabled !== undefined) {
      setClauses.push(`enabled = $${paramIndex++}`);
      params.push(updates.enabled);
    }
    if (updates.metadata) {
      setClauses.push(`metadata = $${paramIndex++}`);
      params.push(JSON.stringify(updates.metadata));
    }
    if (embeddingStr) {
      setClauses.push(`embedding = $${paramIndex++}::vector`);
      params.push(embeddingStr);
    }

    params.push(ruleId);

    const query = `
      UPDATE rules
      SET ${setClauses.join(', ')}, updated_at = NOW()
      WHERE rule_id = $${paramIndex}
      RETURNING *
    `;

    const rows = await this.db.query<Rule>(query, params);

    this.logger.log(`Updated rule: ${ruleId}`);

    return rows[0];
  }

  /**
   * Delete rule (soft delete - marks as deleted)
   */
  async deleteRule(ruleId: string): Promise<void> {
    await this.db.query(
      `UPDATE rules SET enabled = false, updated_at = NOW() WHERE rule_id = $1`,
      [ruleId],
    );

    this.logger.log(`Deleted (disabled) rule: ${ruleId}`);
  }
}
