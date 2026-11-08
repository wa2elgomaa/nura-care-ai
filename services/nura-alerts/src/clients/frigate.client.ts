import { Injectable, Logger } from '@nestjs/common';
import { HttpService } from '@nestjs/axios';
import { ConfigService } from '@nestjs/config';
import { AxiosResponse } from 'axios';
import { firstValueFrom } from 'rxjs';
import { Readable } from 'stream';

export interface ExportClipParams {
  camera: string;
  start_time: Date;
  end_time: Date;
  playback?: 'realtime' | 'timelapse';
}

@Injectable()
export class FrigateClient {
  private readonly logger = new Logger(FrigateClient.name);
  private readonly frigateUrl: string;
  private readonly timeout: number;

  constructor(
    private readonly httpService: HttpService,
    private readonly configService: ConfigService,
  ) {
    this.frigateUrl = this.configService.get<string>('FRIGATE_URL', 'http://frigate:5000');
    this.timeout = parseInt(this.configService.get<string>('FRIGATE_TIMEOUT', '60000'), 10);
  }

  /**
   * Export a video clip from Frigate
   * @param params Camera, time range, playback speed
   * @returns Readable stream of MP4 video or null if failed
   */
  async exportClip(params: ExportClipParams): Promise<Readable | null> {
    try {
      const startTs = Math.floor(params.start_time.getTime() / 1000);
      const endTs = Math.floor(params.end_time.getTime() / 1000);

      const url = `${this.frigateUrl}/api/export/${params.camera}/start/${startTs}/end/${endTs}`;

      this.logger.log(`Exporting clip: ${params.camera} ${startTs}-${endTs}`);

      const response: AxiosResponse<Readable> = await firstValueFrom(
        this.httpService.get(url, {
          params: { playback: params.playback || 'realtime' },
          responseType: 'stream',
          timeout: this.timeout,
        })
      );

      if (response.status === 200) {
        this.logger.log(`✓ Clip export started for ${params.camera}`);
        return response.data;
      } else {
        this.logger.error(`Frigate export failed with status ${response.status}`);
        return null;
      }
    } catch (error) {
      this.logger.error(`Frigate export failed: ${error.message}`);
      if (error.response) {
        this.logger.error(`Response status: ${error.response.status}`);
        this.logger.error(`Response data: ${JSON.stringify(error.response.data)}`);
      }
      return null;
    }
  }

  /**
   * Check if Frigate has recordings available for a given time
   * @param camera Camera name
   * @param timestamp Time to check
   * @returns true if recordings exist
   */
  async verifyClipAvailable(camera: string, timestamp: Date): Promise<boolean> {
    try {
      const afterTs = Math.floor(timestamp.getTime() / 1000);
      const url = `${this.frigateUrl}/api/${camera}/recordings`;

      const response: AxiosResponse<any[]> = await firstValueFrom(
        this.httpService.get(url, {
          params: { after: afterTs },
          timeout: 5000,
        })
      );

      return response.data && response.data.length > 0;
    } catch (error) {
      this.logger.warn(`Failed to verify clip availability: ${error.message}`);
      return false;
    }
  }

  /**
   * Get Frigate health status
   * @returns true if Frigate is healthy
   */
  async healthCheck(): Promise<boolean> {
    try {
      const response: AxiosResponse = await firstValueFrom(
        this.httpService.get(`${this.frigateUrl}/api/stats`, {
          timeout: 5000,
        })
      );

      return response.status === 200;
    } catch (error) {
      this.logger.error(`Frigate health check failed: ${error.message}`);
      return false;
    }
  }
}
