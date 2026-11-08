import { Injectable, Logger } from '@nestjs/common';
import { HttpService } from '@nestjs/axios';
import { ConfigService } from '@nestjs/config';
import { firstValueFrom } from 'rxjs';
import { Readable } from 'stream';
import { AxiosResponse } from 'axios';

export interface StorageMetadata {
  size: number;
  createdAt: Date;
  path: string;
}

/**
 * Client for nura-storage service
 * Handles all file storage operations via HTTP
 */
@Injectable()
export class StorageClient {
  private readonly logger = new Logger(StorageClient.name);
  private readonly storageUrl: string;

  constructor(
    private readonly httpService: HttpService,
    private readonly configService: ConfigService,
  ) {
    this.storageUrl = this.configService.get<string>(
      'STORAGE_SERVICE_URL',
      'http://nura-storage:3012'
    );
  }

  /**
   * Save a stream to storage
   * @param stream Readable stream
   * @param category Storage category (e.g., 'clips', 'snapshots')
   * @param filename Filename
   * @returns Path to saved file
   */
  async saveStream(
    stream: Readable,
    category: string,
    filename: string
  ): Promise<string> {
    try {
      // Convert stream to buffer for upload
      const chunks: Buffer[] = [];
      for await (const chunk of stream) {
        chunks.push(chunk);
      }
      const buffer = Buffer.concat(chunks);

      return await this.saveBuffer(buffer, category, filename);
    } catch (error) {
      this.logger.error(`Failed to save stream: ${error.message}`);
      throw error;
    }
  }

  /**
   * Save a buffer to storage
   * @param buffer Buffer to save
   * @param category Storage category
   * @param filename Filename
   * @returns Path to saved file
   */
  async saveBuffer(
    buffer: Buffer,
    category: string,
    filename: string
  ): Promise<string> {
    try {
      const FormData = (await import('form-data')).default;
      const formData = new FormData();
      formData.append('file', buffer, filename);

      const response: AxiosResponse<{ path: string; size: number }> =
        await firstValueFrom(
          this.httpService.post(
            `${this.storageUrl}/storage/upload/${category}`,
            formData,
            {
              headers: formData.getHeaders(),
            }
          )
        );

      this.logger.log(
        `✓ Saved to storage: ${category}/${filename} (${response.data.size} bytes)`
      );
      return response.data.path;
    } catch (error) {
      this.logger.error(`Failed to save buffer: ${error.message}`);
      throw error;
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
    try {
      const response: AxiosResponse<StorageMetadata> = await firstValueFrom(
        this.httpService.get(
          `${this.storageUrl}/storage/metadata/${category}/${filename}`
        )
      );

      return response.data;
    } catch (error) {
      this.logger.error(`Failed to get metadata: ${error.message}`);
      throw error;
    }
  }

  /**
   * Get file as stream
   * @param category Storage category
   * @param filename Filename
   * @returns Readable stream
   */
  async getStream(category: string, filename: string): Promise<Readable> {
    try {
      const response: AxiosResponse<Readable> = await firstValueFrom(
        this.httpService.get(
          `${this.storageUrl}/storage/download/${category}/${filename}`,
          {
            responseType: 'stream',
          }
        )
      );

      return response.data;
    } catch (error) {
      this.logger.error(`Failed to get stream: ${error.message}`);
      throw error;
    }
  }

  /**
   * Delete a file
   * @param category Storage category
   * @param filename Filename
   */
  async delete(category: string, filename: string): Promise<void> {
    try {
      await firstValueFrom(
        this.httpService.delete(
          `${this.storageUrl}/storage/${category}/${filename}`
        )
      );

      this.logger.log(`✓ Deleted from storage: ${category}/${filename}`);
    } catch (error) {
      this.logger.error(`Failed to delete: ${error.message}`);
      throw error;
    }
  }

  /**
   * Check if file exists
   * @param category Storage category
   * @param filename Filename
   * @returns true if file exists
   */
  async exists(category: string, filename: string): Promise<boolean> {
    try {
      const metadata = await this.getMetadata(category, filename);
      return metadata !== null;
    } catch {
      return false;
    }
  }

  /**
   * List files in a category
   * @param category Storage category
   * @returns Array of filenames
   */
  async listFiles(category: string): Promise<string[]> {
    try {
      const response: AxiosResponse<string[]> = await firstValueFrom(
        this.httpService.get(`${this.storageUrl}/storage/list/${category}`)
      );

      return response.data;
    } catch (error) {
      this.logger.error(`Failed to list files: ${error.message}`);
      return [];
    }
  }

  /**
   * Get storage statistics
   * @returns Storage stats
   */
  async getStats(): Promise<any> {
    try {
      const response: AxiosResponse = await firstValueFrom(
        this.httpService.get(`${this.storageUrl}/storage/stats`)
      );

      return response.data;
    } catch (error) {
      this.logger.error(`Failed to get stats: ${error.message}`);
      throw error;
    }
  }
}
