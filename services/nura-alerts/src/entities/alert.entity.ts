import { Entity, Column, PrimaryGeneratedColumn, CreateDateColumn, UpdateDateColumn } from 'typeorm';

export enum AlertSeverity {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical',
}

export enum AlertStatus {
  PENDING = 'pending',
  SENT = 'sent',
  ACKNOWLEDGED = 'acknowledged',
  RESOLVED = 'resolved',
  ESCALATED = 'escalated',
}

@Entity('alerts')
export class Alert {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column()
  camera: string;

  @Column()
  violationType: string; // 'violence', 'distress', 'supervision'

  @Column({ type: 'enum', enum: AlertSeverity })
  severity: AlertSeverity;

  @Column({ type: 'enum', enum: AlertStatus, default: AlertStatus.PENDING })
  status: AlertStatus;

  @Column('float')
  confidence: number;

  @Column({ nullable: true })
  personId: string;

  @Column({ default: 1 })
  detectionCount: number;

  @Column('float', { nullable: true })
  confidenceAvg: number;

  @Column('float', { nullable: true })
  confidenceMax: number;

  @Column('text')
  details: string;

  @Column({ type: 'jsonb', nullable: true })
  metadata: any;

  // Week 1: Person identification and context
  @Column({ type: 'jsonb', nullable: true })
  personsInvolved: any[]; // Array of PersonInAlert objects

  @Column({ type: 'jsonb', nullable: true })
  context: any; // AlertContext object

  @Column({ type: 'jsonb', nullable: true })
  evidence: any; // Evidence URLs (snapshot, clip, etc)

  @Column({ nullable: true })
  hash: string; // For deduplication

  @CreateDateColumn()
  firstDetected: Date;

  @UpdateDateColumn()
  lastDetected: Date;

  @Column({ nullable: true })
  acknowledgedAt: Date;

  @Column({ nullable: true })
  acknowledgedBy: string;

  @Column({ nullable: true })
  resolvedAt: Date;

  @Column({ nullable: true })
  escalationLevel: number;
}
