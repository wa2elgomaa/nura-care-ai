import { Module } from '@nestjs/common';
import { ViolationsService } from './violations.service.js';
import { ViolationsController } from './violations.controller.js';

@Module({
  providers: [ViolationsService],
  controllers: [ViolationsController],
  exports: [ViolationsService],
})
export class ViolationsModule {}
