import { Injectable, Logger } from '@nestjs/common';
import axios from 'axios';
import { Alert, AlertSeverity } from '../entities/alert.entity';

interface NotificationChannel {
  type: string;
  enabled: boolean;
}

@Injectable()
export class NotificationsService {
  private readonly logger = new Logger(NotificationsService.name);

  private readonly APPRISE_URL = process.env.APPRISE_URL || 'http://localhost:8000';
  private readonly NTFY_URL = process.env.NTFY_URL || 'http://localhost:80';
  private readonly SMS_ENABLED = process.env.SMS_ENABLED === 'true';

  private readonly ROUTING_RULES: Record<AlertSeverity, string[]> = {
    [AlertSeverity.CRITICAL]: ['push', 'sms', 'email', 'dashboard'],
    [AlertSeverity.HIGH]: ['push', 'email', 'dashboard'],
    [AlertSeverity.MEDIUM]: ['push', 'dashboard'],
    [AlertSeverity.LOW]: ['dashboard'],
  };

  async sendNotification(alert: Alert): Promise<void> {
    const channels = this.getChannelsForSeverity(alert.severity);

    this.logger.log(`📢 Sending ${alert.severity} alert to channels: ${channels.join(', ')}`);

    const promises: Promise<any>[] = [];

    if (channels.includes('push')) {
      promises.push(this.sendPushNotification(alert));
    }

    if (channels.includes('email')) {
      promises.push(this.sendEmail(alert));
    }

    if (channels.includes('sms') && this.SMS_ENABLED) {
      promises.push(this.sendSMS(alert));
    }

    // Dashboard notifications are handled via WebSocket (not implemented here)
    // Would be handled by a separate dashboard service

    await Promise.allSettled(promises);
  }

  private getChannelsForSeverity(severity: AlertSeverity): string[] {
    return this.ROUTING_RULES[severity] || ['dashboard'];
  }

  private async sendPushNotification(alert: Alert): Promise<void> {
    try {
      const message = this.formatPushMessage(alert);

      // Send via ntfy
      await axios.post(`${this.NTFY_URL}/nura-alerts`, message.body, {
        headers: {
          'Title': message.title,
          'Priority': this.getPriority(alert.severity),
          'Tags': this.getTags(alert),
        },
      });

      this.logger.log(`✅ Push notification sent for alert ${alert.id}`);
    } catch (error) {
      this.logger.error(`Failed to send push notification: ${error.message}`);
    }
  }

  private async sendEmail(alert: Alert): Promise<void> {
    try {
      const message = this.formatEmailMessage(alert);

      // Send via Apprise
      await axios.post(`${this.APPRISE_URL}/notify`, {
        body: message.body,
        title: message.title,
        type: 'info',
        tag: 'email',
      });

      this.logger.log(`✅ Email sent for alert ${alert.id}`);
    } catch (error) {
      this.logger.error(`Failed to send email: ${error.message}`);
    }
  }

  private async sendSMS(alert: Alert): Promise<void> {
    try {
      const message = this.formatSMSMessage(alert);

      // Send via Apprise (configured with Twilio)
      await axios.post(`${this.APPRISE_URL}/notify`, {
        body: message,
        tag: 'sms',
      });

      this.logger.log(`✅ SMS sent for alert ${alert.id}`);
    } catch (error) {
      this.logger.error(`Failed to send SMS: ${error.message}`);
    }
  }

  private formatPushMessage(alert: Alert): { title: string; body: string } {
    const emoji = this.getEmoji(alert.violationType);
    const title = `${emoji} ${alert.violationType.toUpperCase()} DETECTED`;
    const body = `${alert.camera} - ${alert.details}\nConfidence: ${Math.round(alert.confidence * 100)}%\nDetections: ${alert.detectionCount}`;

    return { title, body };
  }

  private formatEmailMessage(alert: Alert): { title: string; body: string } {
    const title = `[${alert.severity.toUpperCase()}] ${alert.violationType} Detected - ${alert.camera}`;
    const body = `
Incident Details:
- Time: ${alert.firstDetected.toLocaleString()}
- Location: ${alert.camera}
- Type: ${alert.violationType}
- Confidence: ${Math.round(alert.confidence * 100)}%
- Detections: ${alert.detectionCount}
- Status: ONGOING

Details:
${alert.details}

Action Required:
${this.getActionRequired(alert.severity)}

Alert ID: ${alert.id}
    `.trim();

    return { title, body };
  }

  private formatSMSMessage(alert: Alert): string {
    return `[NURA ALERT] ${alert.violationType} detected in ${alert.camera} at ${alert.firstDetected.toLocaleTimeString()}. Confidence: ${Math.round(alert.confidence * 100)}%. Review required.`;
  }

  private getEmoji(violationType: string): string {
    const emojis: Record<string, string> = {
      violence: '🚨',
      distress: '😢',
      supervision: '👁️',
    };
    return emojis[violationType] || '⚠️';
  }

  private getPriority(severity: AlertSeverity): string {
    const priorities: Record<AlertSeverity, string> = {
      [AlertSeverity.CRITICAL]: 'urgent',
      [AlertSeverity.HIGH]: 'high',
      [AlertSeverity.MEDIUM]: 'default',
      [AlertSeverity.LOW]: 'low',
    };
    return priorities[severity];
  }

  private getTags(alert: Alert): string {
    return `${alert.violationType},${alert.severity}`;
  }

  private getActionRequired(severity: AlertSeverity): string {
    const actions: Record<AlertSeverity, string> = {
      [AlertSeverity.CRITICAL]: 'IMMEDIATE staff intervention required.',
      [AlertSeverity.HIGH]: 'Prompt staff attention needed.',
      [AlertSeverity.MEDIUM]: 'Staff review recommended.',
      [AlertSeverity.LOW]: 'Monitor situation.',
    };
    return actions[severity];
  }
}
