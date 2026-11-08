import { Entity, Column, PrimaryGeneratedColumn, CreateDateColumn, ManyToOne, JoinColumn } from 'typeorm';
import { Alert } from './alert.entity';

@Entity('clip_retention')
export class ClipRetention {
  @PrimaryGeneratedColumn('uuid')
  clipId: string;

  @Column({ type: 'uuid' })
  alertId: string;

  @ManyToOne(() => Alert, { onDelete: 'CASCADE' })
  @JoinColumn({ name: 'alert_id' })
  alert: Alert;

  @Column({ length: 500 })
  filePath: string;

  @Column({ type: 'bigint' })
  fileSizeBytes: number;

  @CreateDateColumn()
  createdAt: Date;

  @Column({ type: 'timestamp' })
  expiresAt: Date;

  @Column({ type: 'timestamp', nullable: true })
  deletedAt: Date;
}
