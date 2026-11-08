import {
  Controller,
  Post,
  Get,
  Delete,
  Param,
  Body,
  StreamableFile,
  UploadedFile,
  UseInterceptors,
  HttpException,
  HttpStatus,
  Logger,
} from '@nestjs/common';
import { FileInterceptor } from '@nestjs/platform-express';
import { StorageService } from './storage.service';

interface UploadRequest {
  category: string;
  filename: string;
  data: string; // base64 encoded
}

interface UploadResponse {
  success: boolean;
  path: string;
  size: number;
}

interface FileMetadataResponse {
  exists: boolean;
  size?: number;
  createdAt?: Date;
  path?: string;
}

interface DeleteResponse {
  success: boolean;
  message: string;
}

interface StorageStatsResponse {
  totalSize: number;
  totalSizeFormatted: string;
  fileCount: number;
  categories: Record<string, { size: number; count: number }>;
}

@Controller('storage')
export class StorageController {
  private readonly logger = new Logger(StorageController.name);

  constructor(private readonly storageService: StorageService) {}

  /**
   * Upload a file (multipart/form-data)
   * POST /storage/upload/:category
   */
  @Post('upload/:category')
  @UseInterceptors(FileInterceptor('file'))
  async uploadFile(
    @Param('category') category: string,
    @UploadedFile() file: Express.Multer.File,
  ): Promise<UploadResponse> {
    try {
      const filename = file.originalname;
      const buffer = file.buffer;

      const path = await this.storageService.saveBuffer(buffer, category, filename);
      const metadata = await this.storageService.getMetadata(category, filename);

      this.logger.log(`Uploaded: ${category}/${filename} (${metadata.size} bytes)`);

      return {
        success: true,
        path,
        size: metadata.size,
      };
    } catch (error) {
      this.logger.error(`Upload failed: ${error.message}`);
      throw new HttpException(error.message, HttpStatus.INTERNAL_SERVER_ERROR);
    }
  }

  /**
   * Upload via JSON (base64 encoded data)
   * POST /storage/upload-json
   */
  @Post('upload-json')
  async uploadJson(@Body() request: UploadRequest): Promise<UploadResponse> {
    try {
      const buffer = Buffer.from(request.data, 'base64');
      const path = await this.storageService.saveBuffer(
        buffer,
        request.category,
        request.filename,
      );
      const metadata = await this.storageService.getMetadata(
        request.category,
        request.filename,
      );

      this.logger.log(
        `Uploaded: ${request.category}/${request.filename} (${metadata.size} bytes)`,
      );

      return {
        success: true,
        path,
        size: metadata.size,
      };
    } catch (error) {
      this.logger.error(`Upload failed: ${error.message}`);
      throw new HttpException(error.message, HttpStatus.INTERNAL_SERVER_ERROR);
    }
  }

  /**
   * Download a file
   * GET /storage/download/:category/:filename
   */
  @Get('download/:category/:filename')
  async downloadFile(
    @Param('category') category: string,
    @Param('filename') filename: string,
  ): Promise<StreamableFile> {
    try {
      const exists = await this.storageService.exists(category, filename);
      if (!exists) {
        throw new HttpException('File not found', HttpStatus.NOT_FOUND);
      }

      const stream = await this.storageService.getStream(category, filename);
      return new StreamableFile(stream);
    } catch (error) {
      this.logger.error(`Download failed: ${error.message}`);
      throw new HttpException(error.message, HttpStatus.INTERNAL_SERVER_ERROR);
    }
  }

  /**
   * Get file metadata
   * GET /storage/metadata/:category/:filename
   */
  @Get('metadata/:category/:filename')
  async getMetadata(
    @Param('category') category: string,
    @Param('filename') filename: string,
  ): Promise<FileMetadataResponse> {
    try {
      const exists = await this.storageService.exists(category, filename);
      if (!exists) {
        return { exists: false };
      }

      const metadata = await this.storageService.getMetadata(category, filename);
      return {
        exists: true,
        ...metadata,
      };
    } catch (error) {
      this.logger.error(`Get metadata failed: ${error.message}`);
      throw new HttpException(error.message, HttpStatus.INTERNAL_SERVER_ERROR);
    }
  }

  /**
   * Delete a file
   * DELETE /storage/:category/:filename
   */
  @Delete(':category/:filename')
  async deleteFile(
    @Param('category') category: string,
    @Param('filename') filename: string,
  ): Promise<DeleteResponse> {
    try {
      const exists = await this.storageService.exists(category, filename);
      if (!exists) {
        throw new HttpException('File not found', HttpStatus.NOT_FOUND);
      }

      await this.storageService.delete(category, filename);
      this.logger.log(`Deleted: ${category}/${filename}`);

      return {
        success: true,
        message: `File ${category}/${filename} deleted successfully`,
      };
    } catch (error) {
      this.logger.error(`Delete failed: ${error.message}`);
      throw new HttpException(error.message, HttpStatus.INTERNAL_SERVER_ERROR);
    }
  }

  /**
   * List files in a category
   * GET /storage/list/:category
   */
  @Get('list/:category')
  async listFiles(@Param('category') category: string): Promise<string[]> {
    try {
      return await this.storageService.listFiles(category);
    } catch (error) {
      this.logger.error(`List failed: ${error.message}`);
      throw new HttpException(error.message, HttpStatus.INTERNAL_SERVER_ERROR);
    }
  }

  /**
   * Get storage statistics
   * GET /storage/stats
   */
  @Get('stats')
  async getStats(): Promise<StorageStatsResponse> {
    try {
      const categories = ['clips', 'snapshots', 'exports', 'temp'];
      const stats: Record<string, { size: number; count: number }> = {};
      let totalSize = 0;
      let totalCount = 0;

      for (const category of categories) {
        const size = await this.storageService.getStorageUsage(category);
        const files = await this.storageService.listFiles(category);
        stats[category] = { size, count: files.length };
        totalSize += size;
        totalCount += files.length;
      }

      return {
        totalSize,
        totalSizeFormatted: this.storageService.formatBytes(totalSize),
        fileCount: totalCount,
        categories: stats,
      };
    } catch (error) {
      this.logger.error(`Get stats failed: ${error.message}`);
      throw new HttpException(error.message, HttpStatus.INTERNAL_SERVER_ERROR);
    }
  }

  /**
   * Health check
   * GET /storage/health
   */
  @Get('health')
  async health() {
    return {
      status: 'healthy',
      service: 'nura-storage',
      timestamp: new Date().toISOString(),
    };
  }
}
