#!/usr/bin/env python3
"""
Analyze observed travel times from field measurements and compare with estimated times.

This script compares real-world measurements from observations.md with the estimated
travel times in connections.csv to validate the accuracy of our estimates.
"""

import csv
from pathlib import Path
from typing import Dict, List, Tuple


def parse_time(time_str: str) -> float:
    """
    Parse time string in MM:SS.SS format to minutes.
    
    Args:
        time_str: Time in format "MM:SS.SS" (e.g., "02:23.44")
    
    Returns:
        Time in minutes as float
    """
    parts = time_str.split(':')
    minutes = int(parts[0])
    seconds = float(parts[1])
    return minutes + (seconds / 60)


def load_connections(connections_csv: Path) -> Dict[Tuple[str, str], float]:
    """
    Load connection travel times from CSV.
    
    Returns:
        Dict mapping (from_station_id, to_station_id) -> travel_time_minutes
    """
    connections = {}
    with open(connections_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row['from_station_id'], row['to_station_id'])
            connections[key] = float(row['travel_time_minutes'])
    return connections


def analyze_observations():
    """Main analysis function."""
    
    # Define observed travel segments (from observations.md)
    # Format: (from_station_id, to_station_id, observed_time_str, lap_num)
    observed_travels = [
        ('EW17', 'EW16', '02:23.44', 2),   # Tiong Bahru → Outram Park
        ('EW16', 'EW15', '01:37.11', 4),   # Outram Park → Tanjong Pagar
        ('EW15', 'EW14', '01:41.49', 6),   # Tanjong Pagar → Raffles Place
        ('EW14', 'EW13', '01:31.51', 8),   # Raffles Place → City Hall
        ('EW13', 'EW12', '01:25.12', 10),  # City Hall → Bugis
        ('EW12', 'EW11', '01:29.67', 12),  # Bugis → Lavender
        ('EW11', 'EW10', '02:00.90', 14),  # Lavender → Kallang
        ('EW10', 'EW9', '02:06.07', 16),   # Kallang → Aljunied
        ('EW9', 'EW8', '01:47.96', 18),    # Aljunied → Paya Lebar
        ('EW8', 'EW7', '01:48.24', 20),    # Paya Lebar → Eunos
        ('EW7', 'EW6', '01:49.75', 22),    # Eunos → Kembangan
        ('EW6', 'EW5', '02:29.77', 24),    # Kembangan → Bedok
        ('EW5', 'EW4', '03:12.29', 26),    # Bedok → Tanah Merah
        ('CG', 'CG1', '02:39.55', 29),     # Tanah Merah → Expo (CG line)
    ]
    
    # Observed wait times (for reference)
    observed_waits = [
        ('EW17', '00:23.34', 1),   # Tiong Bahru
        ('EW16', '00:32.37', 3),   # Outram Park
        ('EW15', '00:24.20', 5),   # Tanjong Pagar
        ('EW14', '00:29.62', 7),   # Raffles Place
        ('EW13', '00:28.55', 9),   # City Hall
        ('EW12', '00:50.19', 11),  # Bugis (longer wait)
        ('EW11', '00:24.47', 13),  # Lavender
        ('EW10', '00:34.40', 15),  # Kallang
        ('EW9', '00:32.98', 17),   # Aljunied
        ('EW8', '00:29.08', 19),   # Paya Lebar
        ('EW7', '00:23.43', 21),   # Eunos
        ('EW6', '00:18.90', 23),   # Kembangan
        ('EW5', '00:24.18', 25),   # Bedok
    ]
    
    # Transfer at Tanah Merah
    transfer_wait = ('EW4', 'CG', '04:54.61', 27)  # EW → CG platform transfer
    cg_dwell = ('CG', 'CG', '03:28.46', 28)        # CG line dwell at terminus
    
    # Load estimated times from connections.csv
    connections_csv = Path(__file__).parent.parent / 'data' / 'raw' / 'connections.csv'
    estimated_times = load_connections(connections_csv)
    
    print("=" * 100)
    print("TRAVEL TIME COMPARISON: Observed vs Estimated")
    print("=" * 100)
    print(f"{'Lap':<5} {'Route':<35} {'Observed':<12} {'Estimated':<12} {'Difference':<12} {'Error %':<10}")
    print("-" * 100)
    
    total_observed = 0
    total_estimated = 0
    comparison_count = 0
    errors = []
    
    for from_id, to_id, time_str, lap_num in observed_travels:
        observed_min = parse_time(time_str)
        total_observed += observed_min
        
        # Look up estimated time
        estimated_min = estimated_times.get((from_id, to_id), None)
        
        if estimated_min is not None:
            total_estimated += estimated_min
            comparison_count += 1
            diff = observed_min - estimated_min
            error_pct = (diff / observed_min) * 100 if observed_min > 0 else 0
            errors.append(error_pct)
            
            route = f"{from_id} → {to_id}"
            print(f"{lap_num:<5} {route:<35} {observed_min:>6.2f} min   {estimated_min:>6.2f} min   "
                  f"{diff:>+6.2f} min   {error_pct:>+6.1f}%")
        else:
            route = f"{from_id} → {to_id}"
            print(f"{lap_num:<5} {route:<35} {observed_min:>6.2f} min   {'N/A':<12} {'N/A':<12} {'N/A':<10}")
    
    print("-" * 100)
    print(f"{'TOTAL':<5} {'':<35} {total_observed:>6.2f} min   {total_estimated:>6.2f} min   "
          f"{total_observed - total_estimated:>+6.2f} min   "
          f"{((total_observed - total_estimated) / total_observed * 100):>+6.1f}%")
    print("=" * 100)
    
    # Statistical summary
    if errors:
        avg_error = sum(errors) / len(errors)
        abs_errors = [abs(e) for e in errors]
        avg_abs_error = sum(abs_errors) / len(abs_errors)
        max_error = max(errors)
        min_error = min(errors)
        
        print("\nSTATISTICAL SUMMARY")
        print("=" * 100)
        print(f"Segments compared:        {comparison_count}")
        print(f"Average error:            {avg_error:+.2f}% (positive = observed > estimated)")
        print(f"Average absolute error:   {avg_abs_error:.2f}%")
        print(f"Maximum error:            {max_error:+.2f}%")
        print(f"Minimum error:            {min_error:+.2f}%")
        print("=" * 100)
    
    # Wait time analysis
    print("\nWAIT TIME ANALYSIS")
    print("=" * 100)
    print(f"{'Station ID':<12} {'Wait Time':<12} {'Notes':<50}")
    print("-" * 100)
    
    wait_times = []
    for station_id, time_str, lap_num in observed_waits:
        wait_min = parse_time(time_str)
        wait_times.append(wait_min)
        notes = ""
        if wait_min > 0.8:  # > 48 seconds
            notes = "⚠️  Longer than average"
        print(f"{station_id:<12} {wait_min:>6.2f} min   {notes:<50}")
    
    avg_wait = sum(wait_times) / len(wait_times)
    print("-" * 100)
    print(f"{'AVERAGE':<12} {avg_wait:>6.2f} min")
    print("=" * 100)
    
    # Transfer analysis
    print("\nTRANSFER & DWELL TIME ANALYSIS")
    print("=" * 100)
    transfer_min = parse_time(transfer_wait[2])
    dwell_min = parse_time(cg_dwell[2])
    
    print(f"Transfer wait (EW4 → CG):  {transfer_min:.2f} minutes")
    print(f"  - This includes: walking between platforms + waiting for CG train")
    print(f"  - Suggests physical separation between EW and CG platforms at Tanah Merah")
    print(f"  - **ACTION ITEM**: Add walk_transfer connection in US-103")
    print()
    print(f"CG line dwell at Tanah Merah: {dwell_min:.2f} minutes")
    print(f"  - Unusually long dwell time (typical: 20-40 seconds)")
    print(f"  - Tanah Merah is CG line terminus - longer dwell is expected")
    print("=" * 100)
    
    # Recommendations
    print("\nRECOMMENDATIONS")
    print("=" * 100)
    print("1. ESTIMATED TIMES ACCURACY:")
    if avg_error > 0:
        print(f"   - Estimates are UNDER-predicting by {avg_error:.1f}% on average")
        print(f"   - Consider adjusting MRT speed parameter in generate_connections.py")
        print(f"   - Current: 50 km/h → Suggested: ~{50 * (1 - avg_error/100):.0f} km/h")
    else:
        print(f"   - Estimates are OVER-predicting by {abs(avg_error):.1f}% on average")
        print(f"   - Current speed setting (50 km/h) may be too fast")
    
    print("\n2. DWELL TIME PARAMETER:")
    print(f"   - Current estimate: 0.5 minutes (30 seconds)")
    print(f"   - Observed average wait: {avg_wait:.2f} minutes ({avg_wait*60:.0f} seconds)")
    print(f"   - Note: Wait times include passenger boarding delays, not just dwell")
    
    print("\n3. US-103 WALKING TRANSFERS:")
    print(f"   - Add EW4 ↔ CG connection with ~5 minute transfer time")
    print(f"   - Connection type: 'walk_transfer'")
    print(f"   - Review other interchange stations for similar physical separations")
    
    print("\n4. DATA QUALITY:")
    print(f"   - {comparison_count} of {len(observed_travels)} travel segments validated")
    print(f"   - More field measurements recommended for calibration")
    print(f"   - Consider peak vs off-peak timing variations")
    print("=" * 100)


if __name__ == '__main__':
    analyze_observations()
