#!/usr/bin/env python3
"""
Alert Noise Analyzer - Command Line Interface
Professional CLI tool for analyzing alert noise patterns
"""

import argparse
import sys
import os
from pathlib import Path


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Analyze alert noise patterns and generate recommendations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze alerts and generate report
  analyze-alerts --input alerts.csv --output ./report

  # Specify custom analysis parameters
  analyze-alerts --input alerts.csv --output ./report --window 30

  # Analyze with verbose output
  analyze-alerts --input alerts.csv --output ./report --verbose

For more information: https://github.com/YOUR-USERNAME/alert-noise-framework
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Path to alert data CSV file'
    )
    
    parser.add_argument(
        '--output', '-o',
        default='./output',
        help='Output directory for reports (default: ./output)'
    )
    
    parser.add_argument(
        '--window',
        type=int,
        default=30,
        help='Analysis window in minutes for storm detection (default: 30)'
    )
    
    parser.add_argument(
        '--format',
        choices=['csv', 'json', 'pagerduty'],
        default='csv',
        help='Input data format (default: csv)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Alert Noise Analyzer 1.0.0'
    )
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.input):
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    
    # Create output directory
    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("Alert Noise Reduction Framework")
    print("=" * 60)
    print(f"\nInput:  {args.input}")
    print(f"Output: {args.output}")
    print(f"Format: {args.format}")
    print()
    
    # Import analyzer modules
    try:
        from alert_analyzer import analyze_alerts
        from generate_report import generate_html_report
    except ImportError:
        # Try relative imports for development
        sys.path.insert(0, os.path.dirname(__file__))
        from alert_analyzer import analyze_alerts
        from generate_report import generate_html_report
    
    # Run analysis
    print("Step 1/2: Running analysis...")
    try:
        results_file = analyze_alerts(
            args.input, 
            output_dir=args.output,
            verbose=args.verbose
        )
        print(f"✓ Analysis complete: {results_file}")
    except Exception as e:
        print(f"Error during analysis: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    
    # Generate report
    print("\nStep 2/2: Generating HTML report...")
    try:
        report_file = generate_html_report(
            results_json_path=results_file,
            output_path=os.path.join(args.output, 'alert_noise_report.html')
        )
        print(f"✓ Report generated: {report_file}")
    except Exception as e:
        print(f"Error generating report: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("Analysis Complete!")
    print("=" * 60)
    print(f"\nView your report: {os.path.join(args.output, 'alert_noise_report.html')}")
    print()


if __name__ == '__main__':
    main()
