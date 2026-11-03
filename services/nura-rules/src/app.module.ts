import { Module } from '@nestjs/common';
import { ConfigModule } from './config/config.module.js';
import { EventsModule } from './events/events.module.js';
import { ViolationsModule } from './violations/violations.module.js';

@Module({
  imports: [
    ConfigModule,
    EventsModule,
    ViolationsModule,
  ],
})
export class AppModule {}
