import { Injectable, Logger } from '@nestjs/common';
import { ConfigService } from './config/config.service';
import { createWriteStream, createReadStream } from 'fs';
import { mkdir, stat, unlink, readdir } from 'fs/promises';
import { join } from 'path';
import { Readable } from 'stream';
import { pipeline } from 'stream/promises';

export interface StorageMetadata {
  size: number;
  createdAt: Date;
  path: string;
}

/**
 * Centralized storage service for all file operations
 * Supports multiple backends: local filesystem, S3, GCS, Azure Blob
 * Week 2: Uses local filesystem, designed for easy cloud migration
 */
@Injectable()
export class StorageService {
  private readonly logger = new Logger(StorageService.name);
  private readonly backend: string;
  private readonly baseDir: string;

  constructor(private readonly config: ConfigService) {
    this.backend = this.config.STORAGE_BACKEND;
    this.baseDir = this.config.STORAGE_BASE_PATH;

    this.logger.log(`Storage backend: ${this.backend}`);
    this.logger.log(`Storage base directory: ${this.baseDir}`);
  }

  /**
   * Initialize storage backend
   * Creates necessary directories for local storage
   */
  async initialize(): Promise<void> {
    if (this.backend === StorageBackend.LOCAL) {
      try {
        await mkdir(this.baseDir, { recursive: true });
        this.logger.log(`✓ Storage initialized: ${this.baseDir}`);
      } catch (error) {
        this.logger.error(`Failed to initialize storage: ${error.message}`);
        throw error;
      }
    }
    // TODO: Initialize S3/GCS/Azure clients here
  }

  /**
   * Save a stream to storage
   * @param stream Readable stream to save
   * @param category Storage category (e.g., 'clips', 'snapshots', 'exports')
   * @param filename Filename
   * @returns Full path to saved file
   */
  async saveStream(
    stream: Readable,
    category: string,
    filename: string
  ): Promise<string> {
    const filepath = this.getFilePath(category, filename);

    switch (this.backend) {
      case StorageBackend.LOCAL:
        return await this.saveStreamLocal(stream, filepath);
      case StorageBackend.S3:
        // TODO: Implement S3 upload
        throw new Error('S3 backend not implemented');
      case StorageBackend.GCS:
        // TODO: Implement GCS upload
        throw new Error('GCS backend not implemented');
      case StorageBackend.AZURE:
        // TODO: Implement Azure Blob upload
        throw new Error('Azure backend not implemented');
      default:
        throw new Error(`Unknown storage backend: ${this.backend}`);
    }
  }

  /**
   * Save buffer to storage
   * @param buffer Buffer to save
   * @param category Storage category
   * @param filename Filename
   * @returns Full path to saved file
   */
  async saveBuffer(
    buffer: Buffer,
    category: string,
    filename: string
  ): Promise<string> {
    const filepath = this.getFilePath(category, filename);

    switch (this.backend) {
      case StorageBackend.LOCAL:
        const { writeFile } = await import('fs/promises');
        await this.ensureDirectory(category);
        await writeFile(filepath, buffer);
        this.logger.log(`✓ Saved buffer: ${filepath} (${buffer.length} bytes)`);
        return filepath;
      default:
        // Convert buffer to stream and use saveStream
        const Readable = (await import('stream')).Readable;
        const stream = Readable.from(buffer);
        return await this.saveStream(stream, category, filename);
    }
  }

  /**
   * Get a file as a stream
   * @param category Storage category
   * @param filename Filename
   * @returns Readable stream
   */
  async getStream(category: string, filename: string): Promise<Readable> {
    const filepath = this.getFilePath(category, filename);

    switch (this.backend) {
      case StorageBackend.LOCAL:
        return createReadStream(filepath);
      default:
        throw new Error(`Backend ${this.backend} not implemented for getStream`);
    }
  }

  /**
   * Get file metadata
   * @param category Storage category
   * @param filename Filename
   * @returns File metadata
   */
  async getMetadata(
    category: string,
    filename: string
  ): Promise<StorageMetadata> {
    const filepath = this.getFilePath(category, filename);

    switch (this.backend) {
      case StorageBackend.LOCAL:
        const stats = await stat(filepath);
        return {
          size: stats.size,
          createdAt: stats.birthtime,
          path: filepath,
        };
      default:
        throw new Error(`Backend ${this.backend} not implemented for getMetadata`);
    }
  }

  /**
   * Delete a file
   * @param category Storage category
   * @param filename Filename
   */
  async delete(category: string, filename: string): Promise<void> {
    const filepath = this.getFilePath(category, filename);

    switch (this.backend) {
      case StorageBackend.LOCAL:
        await unlink(filepath);
        this.logger.log(`✓ Deleted: ${filepath}`);
        break;
      default:
        throw new Error(`Backend ${this.backend} not implemented for delete`);
    }
  }

  /**
   * Check if file exists
   * @param category Storage category
   * @param filename Filename
   * @returns true if file exists
   */
  async exists(category: string, filename: string): Promise<boolean> {
    const filepath = this.getFilePath(category, filename);

    switch (this.backend) {
      case StorageBackend.LOCAL:
        try {
          await stat(filepath);
          return true;
        } catch {
          return false;
        }
      default:
        throw new Error(`Backend ${this.backend} not implemented for exists`);
    }
  }

  /**
   * List files in a category
   * @param category Storage category
   * @returns Array of filenames
   */
  async listFiles(category: string): Promise<string[]> {
    const categoryPath = join(this.baseDir, category);

    switch (this.backend) {
      case StorageBackend.LOCAL:
        try {
          const files = await readdir(categoryPath);
          return files;
        } catch {
          return [];
        }
      default:
        throw new Error(`Backend ${this.backend} not implemented for listFiles`);
    }
  }

  /**
   * Get storage usage statistics
   * @param category Optional category to check (null = all storage)
   * @returns Total size in bytes
   */
  async getStorageUsage(category?: string): Promise<number> {
    switch (this.backend) {
      case StorageBackend.LOCAL:
        const targetPath = category ? join(this.baseDir, category) : this.baseDir;
        return await this.getDirectorySize(targetPath);
      default:
        throw new Error(`Backend ${this.backend} not implemented for getStorageUsage`);
    }
  }

  // ========== Private Helper Methods ==========

  private getFilePath(category: string, filename: string): string {
    return join(this.baseDir, category, filename);
  }

  private async ensureDirectory(category: string): Promise<void> {
    const categoryPath = join(this.baseDir, category);
    await mkdir(categoryPath, { recursive: true });
  }

  private async saveStreamLocal(
    stream: Readable,
    filepath: string
  ): Promise<string> {
    // Ensure directory exists
    const dir = filepath.substring(0, filepath.lastIndexOf('/'));
    await mkdir(dir, { recursive: true });

    // Save stream
    const writeStream = createWriteStream(filepath);
    await pipeline(stream, writeStream);

    this.logger.log(`✓ Saved stream: ${filepath}`);
    return filepath;
  }

  private async getDirectorySize(dirPath: string): Promise<number> {
    try {
      const files = await readdir(dirPath, { withFileTypes: true });
      let totalSize = 0;

      for (const file of files) {
        const filePath = join(dirPath, file.name);
        if (file.isDirectory()) {
          totalSize += await this.getDirectorySize(filePath);
        } else {
          const stats = await stat(filePath);
          totalSize += stats.size;
        }
      }

      return totalSize;
    } catch {
      return 0;
    }
  }

  /**
   * Format bytes to human-readable string
   */
  formatBytes(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  }
}
