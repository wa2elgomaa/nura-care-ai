import { Injectable, Logger } from '@nestjs/common';
import axios, { AxiosInstance } from 'axios';

/**
 * Frigate API Client
 *
 * Fetches frames, events, and recordings from Frigate NVR
 */
@Injectable()
export class FrigateClientService {
  private readonly logger = new Logger(FrigateClientService.name);
  private readonly client: AxiosInstance;
  private readonly frigateUrl: string;

  constructor() {
    this.frigateUrl = process.env.FRIGATE_API || 'http://localhost:5000';
    this.client = axios.create({
      baseURL: this.frigateUrl,
      timeout: 10000,
    });
  }

  /**
   * Get latest frame from a camera
   */
  async getLatestFrame(camera: string): Promise<Buffer> {
    try {
      const response = await this.client.get(`/api/${camera}/latest.jpg`, {
        responseType: 'arraybuffer',
      });
      return Buffer.from(response.data);
    } catch (error) {
      this.logger.error(`Failed to fetch frame from ${camera}: ${error.message}`);
      throw error;
    }
  }

  /**
   * Get snapshot for a specific event
   */
  async getEventSnapshot(eventId: string): Promise<Buffer> {
    try {
      const response = await this.client.get(`/api/events/${eventId}/snapshot.jpg`, {
        responseType: 'arraybuffer',
      });
      return Buffer.from(response.data);
    } catch (error) {
      this.logger.error(`Failed to fetch snapshot for event ${eventId}: ${error.message}`);
      throw error;
    }
  }

  /**
   * Get event details
   */
  async getEvent(eventId: string): Promise<any> {
    try {
      const response = await this.client.get(`/api/events/${eventId}`);
      return response.data;
    } catch (error) {
      this.logger.error(`Failed to fetch event ${eventId}: ${error.message}`);
      throw error;
    }
  }

  /**
   * Get recent events for a camera
   */
  async getRecentEvents(camera: string, limit: number = 10): Promise<any[]> {
    try {
      const response = await this.client.get(`/api/events`, {
        params: {
          camera,
          limit,
        },
      });
      return response.data;
    } catch (error) {
      this.logger.error(`Failed to fetch recent events for ${camera}: ${error.message}`);
      throw error;
    }
  }

  /**
   * Get Frigate stats
   */
  async getStats(): Promise<any> {
    try {
      const response = await this.client.get('/api/stats');
      return response.data;
    } catch (error) {
      this.logger.error(`Failed to fetch Frigate stats: ${error.message}`);
      throw error;
    }
  }

  /**
   * Get config
   */
  async getConfig(): Promise<any> {
    try {
      const response = await this.client.get('/api/config');
      return response.data;
    } catch (error) {
      this.logger.error(`Failed to fetch Frigate config: ${error.message}`);
      throw error;
    }
  }

  /**
   * Health check
   */
  async isHealthy(): Promise<boolean> {
    try {
      await this.client.get('/api/stats');
      return true;
    } catch (error) {
      return false;
    }
  }
}
