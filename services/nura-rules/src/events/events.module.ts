import { Module } from '@nestjs/common';
import { EventsController } from './events.controller.js';
import { ViolationsModule } from '../violations/violations.module.js';

@Module({
  imports: [ViolationsModule],
  controllers: [EventsController],
})
export class EventsModule {}
