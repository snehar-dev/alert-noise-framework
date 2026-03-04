#!/usr/bin/env python3
"""
Alert Noise Reduction Framework
Analyzes alert history and identifies noise patterns
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import json


class AlertNoiseAnalyzer:
    """Main analyzer for detecting alert noise patterns"""
    
    def __init__(self, csv_path):
        """Load alert data from CSV"""
        self.df = pd.read_csv(csv_path)
        self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
        self.df = self.df.sort_values('timestamp')
        
        self.results = {
            'duplicates': [],
            'flapping': [],
            'storms': [],
            'low_value': [],
            'severity_issues': [],
            'summary': {}
        }
    
    def analyze_all(self):
        """Run all analysis modules"""
        print("🔍 Starting Alert Noise Analysis...")
        print(f"📊 Loaded {len(self.df)} alerts")
        print(f"📅 Date range: {self.df['timestamp'].min()} to {self.df['timestamp'].max()}")
        print()
        
        self.detect_duplicates()
        self.detect_flapping()
        self.detect_alert_storms()
        self.identify_low_value()
        self.detect_severity_issues()
        self.generate_summary()
        
        return self.results
    
    def detect_duplicates(self):
        """Detect duplicate alerts (same issue, different sources)"""
        print("🔎 MODULE 1: Detecting Duplicate Alerts...")
        
        # Group alerts by time window and look for similar names
        duplicates = defaultdict(list)
        
        # Find alerts with similar names (fuzzy matching)
        alert_groups = defaultdict(list)
        for alert in self.df['alert_name'].unique():
            # Normalize: remove hyphens, underscores, convert to lowercase
            normalized = alert.lower().replace('-', '').replace('_', '').replace(' ', '')
            # Group by key words (cpu, memory, disk, etc.)
            if 'cpu' in normalized:
                alert_groups['cpu'].append(alert)
            elif 'memory' in normalized or 'mem' in normalized:
                alert_groups['memory'].append(alert)
            elif 'disk' in normalized:
                alert_groups['disk'].append(alert)
        
        # Analyze each group
        for group_name, alerts in alert_groups.items():
            if len(alerts) > 1:
                # Count how many times these alerts fire together
                sources = set()
                for alert in alerts:
                    alert_sources = self.df[self.df['alert_name'] == alert]['source'].unique()
                    sources.update(alert_sources)
                
                duplicates[group_name] = {
                    'alerts': alerts,
                    'sources': list(sources),
                    'count': len(alerts),
                    'recommendation': f"Consolidate {len(alerts)} alerts into 1 unified '{group_name}' alert"
                }
        
        self.results['duplicates'] = duplicates
        print(f"   Found {len(duplicates)} duplicate alert groups")
        print()
    
    def detect_flapping(self):
        """Detect alerts that fire and resolve repeatedly (flapping)"""
        print("🔎 MODULE 2: Detecting Flapping Alerts...")
        
        flapping_alerts = {}
        
        for alert_name in self.df['alert_name'].unique():
            alert_data = self.df[self.df['alert_name'] == alert_name].sort_values('timestamp')
            
            # Count status changes
            if len(alert_data) < 10:
                continue
            
            # Calculate time between events
            time_diffs = alert_data['timestamp'].diff()
            
            # Flapping if median time between events is < 15 minutes and >10 events
            if len(alert_data) > 10:
                median_interval = time_diffs.median()
                if pd.notna(median_interval) and median_interval < timedelta(minutes=15):
                    # Check for fire/resolve pattern
                    status_changes = (alert_data['status'] != alert_data['status'].shift()).sum()
                    
                    if status_changes > 5:  # Multiple status changes
                        flapping_alerts[alert_name] = {
                            'event_count': len(alert_data),
                            'median_interval_minutes': median_interval.total_seconds() / 60,
                            'status_changes': status_changes,
                            'recommendation': 'Add 15-minute cool-down period or adjust threshold'
                        }
        
        self.results['flapping'] = flapping_alerts
        print(f"   Found {len(flapping_alerts)} flapping alerts")
        print()
    
    def detect_alert_storms(self):
        """Detect alert storms (cascading failures)"""
        print("🔎 MODULE 3: Detecting Alert Storms...")
        
        storms = []
        
        # Look for time windows with >10 alerts in 30 minutes
        self.df['time_bucket'] = self.df['timestamp'].dt.floor('30min')
        storm_buckets = self.df.groupby('time_bucket').size()
        
        high_volume_buckets = storm_buckets[storm_buckets > 10]
        
        for bucket_time, count in high_volume_buckets.items():
            bucket_data = self.df[self.df['time_bucket'] == bucket_time]
            
            # Get unique alerts in this storm
            unique_alerts = bucket_data['alert_name'].nunique()
            
            # Identify potential root cause (first critical alert)
            critical_alerts = bucket_data[bucket_data['severity'] == 'critical'].sort_values('timestamp')
            root_cause = critical_alerts.iloc[0]['alert_name'] if len(critical_alerts) > 0 else bucket_data.iloc[0]['alert_name']
            
            storms.append({
                'timestamp': bucket_time,
                'total_alerts': int(count),
                'unique_alerts': int(unique_alerts),
                'likely_root_cause': root_cause,
                'recommendation': f'Create alert dependency: suppress downstream alerts when {root_cause} fires'
            })
        
        self.results['storms'] = storms
        print(f"   Found {len(storms)} alert storms")
        print()
    
    def identify_low_value(self):
        """Identify alerts that are never acted upon"""
        print("🔎 MODULE 4: Identifying Low-Value Alerts...")
        
        low_value = {}
        
        # Heuristics for low-value alerts:
        # 1. Low severity with high frequency
        # 2. Always firing, never resolved
        # 3. Very short duration (auto-resolved)
        
        for alert_name in self.df['alert_name'].unique():
            alert_data = self.df[self.df['alert_name'] == alert_name]
            
            avg_duration = alert_data['duration_minutes'].mean()
            severity = alert_data['severity'].mode()[0] if len(alert_data) > 0 else 'unknown'
            fire_count = len(alert_data)
            
            # Low severity + high frequency + short duration = noise
            if severity == 'low' and fire_count > 10 and avg_duration < 10:
                low_value[alert_name] = {
                    'fire_count': int(fire_count),
                    'avg_duration_minutes': float(avg_duration),
                    'severity': severity,
                    'recommendation': 'Consider deleting - appears to be informational noise'
                }
        
        self.results['low_value'] = low_value
        print(f"   Found {len(low_value)} low-value alerts")
        print()
    
    def detect_severity_issues(self):
        """Detect alerts with incorrect severity classification"""
        print("🔎 MODULE 5: Detecting Severity Misclassification...")
        
        severity_issues = {}
        
        for alert_name in self.df['alert_name'].unique():
            alert_data = self.df[self.df['alert_name'] == alert_name]
            
            severity = alert_data['severity'].mode()[0] if len(alert_data) > 0 else 'unknown'
            avg_duration = alert_data['duration_minutes'].mean()
            
            # Critical alerts that auto-resolve quickly might not be critical
            if severity == 'critical' and avg_duration < 5:
                severity_issues[alert_name] = {
                    'current_severity': severity,
                    'avg_duration_minutes': float(avg_duration),
                    'suggested_severity': 'medium',
                    'recommendation': 'Downgrade severity - resolves too quickly to be critical'
                }
            
            # Medium/Low alerts with long duration might need escalation
            elif severity in ['medium', 'low'] and avg_duration > 120:
                severity_issues[alert_name] = {
                    'current_severity': severity,
                    'avg_duration_minutes': float(avg_duration),
                    'suggested_severity': 'high',
                    'recommendation': 'Upgrade severity - persists for extended periods'
                }
        
        self.results['severity_issues'] = severity_issues
        print(f"   Found {len(severity_issues)} severity misclassifications")
        print()
    
    def generate_summary(self):
        """Generate executive summary"""
        total_alerts = len(self.df)
        days = (self.df['timestamp'].max() - self.df['timestamp'].min()).days
        daily_avg = total_alerts / days if days > 0 else total_alerts
        
        # Calculate reduction potential
        duplicate_reduction = sum(len(v['alerts']) - 1 for v in self.results['duplicates'].values())
        flapping_reduction = len(self.results['flapping']) * 0.7  # Estimate 70% reduction from cool-down
        storm_reduction = sum(s['total_alerts'] - 3 for s in self.results['storms'])  # Keep 3 alerts per storm
        low_value_reduction = len(self.results['low_value'])
        
        total_reduction = duplicate_reduction + flapping_reduction + storm_reduction + low_value_reduction
        reduction_percentage = (total_reduction / daily_avg) * 100 if daily_avg > 0 else 0
        
        self.results['summary'] = {
            'analysis_period_days': int(days),
            'total_alerts_analyzed': int(total_alerts),
            'current_daily_avg': float(daily_avg),
            'noise_identified': {
                'duplicates': int(duplicate_reduction),
                'flapping': int(flapping_reduction),
                'storms': int(storm_reduction),
                'low_value': int(low_value_reduction),
                'total': int(total_reduction)
            },
            'recommended_daily_avg': float(daily_avg - (total_reduction / days)),
            'reduction_percentage': float(reduction_percentage),
            'projected_impact': {
                'time_saved_hours_per_month': float(total_reduction * 0.25),  # 15min per alert
                'mttr_improvement_percentage': 30,  # Fewer distractions
                'cost_savings_per_year': int(total_reduction * 0.25 * 12 * 150)  # $150/hour engineer cost
            }
        }
        
        print("=" * 60)
        print("📊 ANALYSIS COMPLETE")
        print("=" * 60)
        print(f"Noise Reduction Potential: {reduction_percentage:.1f}%")
        print(f"Current: {daily_avg:.1f} alerts/day → Recommended: {self.results['summary']['recommended_daily_avg']:.1f} alerts/day")
        print()


def main():
    """Main entry point"""
    import sys
    
    csv_path = sys.argv[1] if len(sys.argv) > 1 else 'sample_data.csv'
    
    analyzer = AlertNoiseAnalyzer(csv_path)
    results = analyzer.analyze_all()
    
    # Save results to JSON
    with open('analysis_results.json', 'w') as f:
        # Convert results to JSON-serializable format
        json_results = json.loads(json.dumps(results, default=str))
        json.dump(json_results, f, indent=2)
    
    print(f"✅ Results saved to analysis_results.json")
    
    return results


def analyze_alerts(csv_file, output_dir='.', verbose=False):
    """
    CLI-compatible analysis function
    
    Args:
        csv_file: Path to CSV file
        output_dir: Output directory for results
        verbose: Enable verbose output
        
    Returns:
        Path to results JSON file
    """
    import os
    
    if verbose:
        print(f"Loading alert data from: {csv_file}")
    
    analyzer = AlertNoiseAnalyzer(csv_file)
    results = analyzer.analyze_all()
    
    # Save results
    results_file = os.path.join(output_dir, 'analysis_results.json')
    with open(results_file, 'w') as f:
        json_results = json.loads(json.dumps(results, default=str))
        json.dump(json_results, f, indent=2)
    
    if verbose:
        print(f"Results saved to: {results_file}")
    
    return results_file


if __name__ == '__main__':
    main()
