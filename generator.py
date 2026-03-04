#!/usr/bin/env python3
"""
Alert Data Generator - Synthetic Alert Creation Tool
Generates realistic alert patterns for testing and demonstration
"""

import argparse
import csv
import random
import sys
from datetime import datetime, timedelta


def generate_alerts(days=30, noise_level='medium', output_file='sample_data.csv'):
    """
    Generate synthetic alert data with realistic patterns
    
    Args:
        days: Number of days to generate data for
        noise_level: 'low', 'medium', or 'high' alert volume
        output_file: Output CSV filename
    """
    
    # Alert volume multipliers based on noise level
    volume_config = {
        'low': {'base': 50, 'duplicates': 2, 'flapping': 1, 'noise': 2},
        'medium': {'base': 120, 'duplicates': 4, 'flapping': 3, 'noise': 5},
        'high': {'base': 200, 'duplicates': 5, 'flapping': 4, 'noise': 6}
    }
    
    config = volume_config.get(noise_level, volume_config['medium'])
    
    print(f"Generating {days} days of alert data (noise level: {noise_level})...")
    
    # Alert templates - realistic monitoring patterns
    alert_templates = {
        'cpu_duplicates': [
            ('cpu-high-prometheus', 'critical', 'prometheus'),
            ('cpu-utilization-cloudwatch', 'critical', 'cloudwatch'),
            ('high-cpu-datadog', 'critical', 'datadog'),
            ('cpu-alert-grafana', 'critical', 'grafana'),
            ('cpu-threshold-nagios', 'critical', 'nagios'),
        ],
        'memory_duplicates': [
            ('memory-threshold-exceeded', 'high', 'grafana'),
            ('high-memory-usage', 'high', 'prometheus'),
            ('memory-alert-cloudwatch', 'high', 'cloudwatch'),
            ('mem-utilization-high', 'high', 'datadog'),
        ],
        'disk_duplicates': [
            ('disk-space-critical', 'critical', 'splunk'),
            ('filesystem-full', 'critical', 'nagios'),
            ('disk-utilization-high', 'critical', 'cloudwatch'),
            ('disk-alert-prometheus', 'critical', 'prometheus'),
        ],
        'flapping': [
            ('disk-80-percent', 'medium', 'prometheus'),
            ('api-latency-threshold', 'high', 'datadog'),
            ('memory-swap-high', 'medium', 'prometheus'),
        ],
        'database_storm': [
            ('database-connection-failed', 'critical', 'app-monitor'),
            ('api-500-errors', 'critical', 'nginx'),
            ('queue-backup', 'high', 'rabbitmq'),
            ('cache-miss-rate-high', 'high', 'redis'),
            ('slow-queries', 'medium', 'mysql'),
            ('connection-pool-exhausted', 'high', 'app'),
            ('backend-timeout', 'high', 'loadbalancer'),
        ],
        'noise': [
            ('test-alert-dev', 'low', 'test-system'),
            ('info-deployment-success', 'low', 'ci-cd'),
            ('backup-completed', 'low', 'backup-system'),
            ('certificate-expiry-90days', 'low', 'security'),
            ('health-check-success', 'low', 'monitoring'),
            ('log-rotation-complete', 'low', 'system'),
        ],
        'important': [
            ('service-down', 'critical', 'healthcheck'),
            ('payment-processing-failed', 'critical', 'payment-gateway'),
            ('database-replication-lag', 'high', 'database'),
        ],
    }
    
    start_date = datetime.now() - timedelta(days=days)
    alerts = []
    
    for day in range(days):
        current_date = start_date + timedelta(days=day)
        
        # CPU duplicates
        for _ in range(config['duplicates']):
            for alert_name, severity, source in alert_templates['cpu_duplicates']:
                timestamp = current_date + timedelta(
                    hours=random.randint(0, 23), 
                    minutes=random.randint(0, 59)
                )
                alerts.append({
                    'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'alert_name': alert_name,
                    'severity': severity,
                    'status': 'firing',
                    'source': source,
                    'duration_minutes': random.randint(15, 120)
                })
        
        # Memory duplicates
        for _ in range(config['duplicates'] - 1):
            for alert_name, severity, source in alert_templates['memory_duplicates']:
                timestamp = current_date + timedelta(
                    hours=random.randint(0, 23), 
                    minutes=random.randint(0, 59)
                )
                alerts.append({
                    'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'alert_name': alert_name,
                    'severity': severity,
                    'status': 'firing',
                    'source': source,
                    'duration_minutes': random.randint(20, 90)
                })
        
        # Disk duplicates
        for _ in range(config['duplicates'] - 2):
            for alert_name, severity, source in alert_templates['disk_duplicates']:
                timestamp = current_date + timedelta(
                    hours=random.randint(0, 23), 
                    minutes=random.randint(0, 59)
                )
                alerts.append({
                    'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'alert_name': alert_name,
                    'severity': severity,
                    'status': 'firing',
                    'source': source,
                    'duration_minutes': random.randint(30, 180)
                })
        
        # Flapping alerts
        for _ in range(config['flapping'] * 13):
            for alert_name, severity, source in alert_templates['flapping']:
                timestamp = current_date + timedelta(
                    hours=random.randint(0, 23), 
                    minutes=random.randint(0, 59)
                )
                status = random.choice(['firing', 'resolved'])
                alerts.append({
                    'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'alert_name': alert_name,
                    'severity': severity,
                    'status': status,
                    'source': source,
                    'duration_minutes': random.randint(1, 10) if status == 'resolved' else random.randint(5, 15)
                })
        
        # Alert storms (periodic)
        if day % 10 == 5:
            storm_time = current_date + timedelta(hours=random.randint(10, 16))
            for alert_name, severity, source in alert_templates['database_storm']:
                timestamp = storm_time + timedelta(minutes=random.randint(0, 30))
                alerts.append({
                    'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'alert_name': alert_name,
                    'severity': severity,
                    'status': 'firing',
                    'source': source,
                    'duration_minutes': random.randint(45, 180)
                })
        
        # Low-value noise
        for _ in range(config['noise']):
            for alert_name, severity, source in alert_templates['noise']:
                timestamp = current_date + timedelta(
                    hours=random.randint(0, 23), 
                    minutes=random.randint(0, 59)
                )
                alerts.append({
                    'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'alert_name': alert_name,
                    'severity': severity,
                    'status': 'firing',
                    'source': source,
                    'duration_minutes': random.randint(1, 5)
                })
        
        # Important alerts (good signal)
        for _ in range(random.randint(2, 3)):
            alert_name, severity, source = random.choice(alert_templates['important'])
            timestamp = current_date + timedelta(
                hours=random.randint(0, 23), 
                minutes=random.randint(0, 59)
            )
            alerts.append({
                'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'alert_name': alert_name,
                'severity': severity,
                'status': 'firing',
                'source': source,
                'duration_minutes': random.randint(15, 120)
            })
    
    # Sort by timestamp
    alerts.sort(key=lambda x: x['timestamp'])
    
    # Write to CSV
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['timestamp', 'alert_name', 'severity', 'status', 'source', 'duration_minutes']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(alerts)
    
    print(f"\n✓ Generated {len(alerts)} alerts over {days} days")
    print(f"  Average: {len(alerts)/days:.1f} alerts/day")
    print(f"  Output: {output_file}")
    print()
    
    # Print breakdown
    print("Alert Pattern Breakdown:")
    print(f"  CPU duplicates:   ~{config['duplicates'] * 5 * days} alerts")
    print(f"  Memory duplicates: ~{(config['duplicates']-1) * 4 * days} alerts")
    print(f"  Disk duplicates:   ~{(config['duplicates']-2) * 4 * days} alerts")
    print(f"  Flapping alerts:   ~{config['flapping'] * 13 * 3 * days} events")
    print(f"  Low-value noise:   ~{config['noise'] * 6 * days} alerts")
    print(f"  Alert storms:      ~{(days//10) * 7} alerts")
    print(f"  Important (keep):  ~{2.5 * days:.0f} alerts")
    print()


def main():
    """CLI entry point for alert generator"""
    parser = argparse.ArgumentParser(
        description='Generate synthetic alert data for testing and demonstration',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate 30 days of medium-noise alerts
  generate-alerts --days 30 --noise medium --output alerts.csv

  # Generate high-volume alert data
  generate-alerts --days 60 --noise high --output high_volume.csv

  # Generate low-noise baseline
  generate-alerts --days 7 --noise low --output baseline.csv

Noise Levels:
  low    - ~50 alerts/day  (minimal duplication)
  medium - ~120 alerts/day (moderate noise)
  high   - ~200 alerts/day (high noise, realistic for enterprise)
        """
    )
    
    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='Number of days to generate data for (default: 30)'
    )
    
    parser.add_argument(
        '--noise',
        choices=['low', 'medium', 'high'],
        default='medium',
        help='Alert noise level (default: medium)'
    )
    
    parser.add_argument(
        '--output', '-o',
        default='sample_data.csv',
        help='Output CSV filename (default: sample_data.csv)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Alert Generator 1.0.0'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Alert Data Generator")
    print("=" * 60)
    print()
    
    try:
        generate_alerts(
            days=args.days,
            noise_level=args.noise,
            output_file=args.output
        )
    except Exception as e:
        print(f"Error generating alerts: {e}", file=sys.stderr)
        sys.exit(1)
    
    print("=" * 60)
    print("Generation Complete!")
    print("=" * 60)
    print(f"\nUse this data with: analyze-alerts --input {args.output}")
    print()


if __name__ == '__main__':
    main()
