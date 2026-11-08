import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { StreamProcessorModule } from './stream-processor/stream-processor.module';
import { HealthController } from './health.controller';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
    }),
    StreamProcessorModule,
  ],
  controllers: [HealthController],
})
export class AppModule {}
