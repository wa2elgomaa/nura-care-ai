import { Injectable, OnModuleInit, Logger } from '@nestjs/common';
import { pipeline, FeatureExtractionPipeline } from '@xenova/transformers';
import { ConfigService } from '../config/config.service.js';

/**
 * Embeddings Service
 * Generates vector embeddings for text using sentence-transformers
 * Model: all-MiniLM-L6-v2 (384 dimensions, fast CPU inference)
 */
@Injectable()
export class EmbeddingsService implements OnModuleInit {
  private readonly logger = new Logger(EmbeddingsService.name);
  private extractor: FeatureExtractionPipeline | null = null;

  constructor(private readonly config: ConfigService) { }

  async onModuleInit() {
    this.logger.log('Initializing embedding model...');
    this.logger.log(`Model: ${this.config.embeddingModel}`);

    try {
      // Load sentence-transformers model (ONNX format)
      this.extractor = await pipeline(
        'feature-extraction',
        this.config.embeddingModel
      );

      this.logger.log('✓ Embedding model loaded successfully');
    } catch (error) {
      this.logger.error('✗ Failed to load embedding model:', error);
      throw error;
    }
  }

  /**
   * Generate embedding vector for text
   * @param text Text to embed (max 512 tokens)
   * @returns 384-dimensional vector
   */
  async generateEmbedding(text: string): Promise<number[]> {
    if (!this.extractor) {
      throw new Error('Embedding model not initialized');
    }

    if (!text || text.trim().length === 0) {
      throw new Error('Text cannot be empty');
    }

    try {
      const start = Date.now();

      // Generate embedding
      const output = await this.extractor(text, {
        pooling: 'mean',
        normalize: true,
      });

      // Extract the embedding array
      const embedding = Array.from(output.data) as number[];

      const duration = Date.now() - start;
      this.logger.debug(`Generated embedding in ${duration}ms`);

      if (embedding.length !== this.config.embeddingDimensions) {
        throw new Error(
          `Expected ${this.config.embeddingDimensions} dimensions, got ${embedding.length}`
        );
      }

      return embedding;
    } catch (error) {
      this.logger.error('Failed to generate embedding:', error);
      throw error;
    }
  }

  /**
   * Generate embeddings for multiple texts (batch)
   * @param texts Array of texts
   * @returns Array of embedding vectors
   */
  async generateEmbeddings(texts: string[]): Promise<number[][]> {
    const embeddings: number[][] = [];

    for (const text of texts) {
      const embedding = await this.generateEmbedding(text);
      embeddings.push(embedding);
    }

    return embeddings;
  }

  /**
   * Compute cosine similarity between two vectors
   * @param a Vector A
   * @param b Vector B
   * @returns Similarity score (0-1, higher = more similar)
   */
  cosineSimilarity(a: number[], b: number[]): number {
    if (a.length !== b.length) {
      throw new Error('Vectors must have same length');
    }

    let dotProduct = 0;
    let normA = 0;
    let normB = 0;

    for (let i = 0; i < a.length; i++) {
      dotProduct += a[i] * b[i];
      normA += a[i] * a[i];
      normB += b[i] * b[i];
    }

    return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
  }
}
