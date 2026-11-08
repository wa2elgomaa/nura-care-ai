import { Entity, Column, PrimaryGeneratedColumn, CreateDateColumn, ManyToOne, JoinColumn } from 'typeorm';
import { Alert } from './alert.entity';

export enum ClipStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
}

@Entity('clip_processing_queue')
export class ClipProcessingQueue {
  @PrimaryGeneratedColumn('uuid')
  queueId: string;

  @Column({ type: 'uuid' })
  alertId: string;

  @ManyToOne(() => Alert, { onDelete: 'CASCADE' })
  @JoinColumn({ name: 'alert_id' })
  alert: Alert;

  @Column()
  cameraId: string;

  @Column({ type: 'timestamp' })
  incidentTimestamp: Date;

  @Column({ default: 10 })
  beforeSeconds: number;

  @Column({ default: 20 })
  afterSeconds: number;

  @Column({ type: 'enum', enum: ClipStatus, default: ClipStatus.PENDING })
  status: ClipStatus;

  @Column({ default: 0 })
  retryCount: number;

  @Column({ type: 'text', nullable: true })
  errorMessage: string;

  @CreateDateColumn()
  createdAt: Date;

  @Column({ type: 'timestamp', nullable: true })
  processedAt: Date;
}
